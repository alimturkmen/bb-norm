
import math
import sys
from glob import glob
from typing import Dict, List
from tqdm import tqdm

import tensorflow as tf

import bb_normalizer
import bb_parser
import context_parser
import defs
import utility
import w2v_parser
from bb_normalizer import ExactMatch
from context_embedding import ContextEmbedding
from entity import BiotopeContext, Biotope, EntityType, SearchEntity, BiotopeFeatures


def cos_sim(tensor1, tensor2):
    dot_prod = tf.reduce_sum(tensor1 * tensor2)
    len_t1 = math.sqrt(tf.reduce_sum(tensor1 * tensor1))
    len_t2 = math.sqrt(tf.reduce_sum(tensor2 * tensor2))
    return float(dot_prod / (len_t1 * len_t2))


def context_match_term(search_entity: str, biotope_context: BiotopeContext, biotopes: Dict[str, Biotope],
                       context_embedder: ContextEmbedding, exact_matcher: ExactMatch):
    curr_sim = 0
    matched_term = '000000'
    matched_name = None

    c_embed = tf.convert_to_tensor(context_embedder.sentence_embed([biotope_context.sentence]))
    #s_embed = tf.convert_to_tensor(context_embedder.sentence_embed([search_entity]))
    s_embed = context_embedder.name_embed(search_entity)
    n_embed = context_embedder.name_embed(search_entity)

    cos_sims = []
    for term in biotopes:

        context_sim, surface_sim, name_sim = 0, 0, 0
        if biotopes[term].context_embedding is not None :
            context_sim = cos_sim(c_embed, biotopes[term].context_embedding)
        if biotopes[term].surface_embedding is not None :
            surface_sim = cos_sim(s_embed, biotopes[term].surface_embedding)
        if biotopes[term].name_embedding is not None :
            name_sim = cos_sim(n_embed, biotopes[term].name_embedding)
        '''
        if not (context_sim and surface_sim and name_sim):
            res =exact_matcher.weighted_match_term(SearchEntity(None, None, search_entity, None, None))
            if res['score'] > 0 : matched_term = res['ref']
            break
        '''
        # prev_weights = 0.33, 0.33, 0.34
        #local_sim = 0.30*context_sim + 0.25*surface_sim + 0.45*name_sim #+ 0.34*match_score/3
        name_surface_avg = (0.4*surface_sim+0.6*name_sim)

        if context_sim == 0: local_sim = 0.15 + 0.75*name_surface_avg
        else: local_sim = 0.25*context_sim + 0.75*name_surface_avg

        if local_sim > curr_sim and local_sim > 0.5:
            cos_sims = [context_sim, surface_sim, name_sim]
            curr_sim = local_sim
            matched_term = term
            matched_name = biotopes[term].name

    if curr_sim == 0:
        res =exact_matcher.weighted_match_term(SearchEntity(None, None, search_entity, None, None))
        if res['score'] > 0 : matched_term = res['ref']

    biotopes[matched_term].add_context(BiotopeFeatures(surf=search_entity, sent=biotope_context.sentence))
    print(f"{search_entity}\tscore:{cos_sims}\tmatch:{matched_term}")
    return matched_term


def run(save_file_path: str, load_file_path: str):

    dev_txt_files = sorted(glob(defs.DEV_TXT_FILES))
    dev_a1_files = sorted(glob(defs.DEV_FILES))
    dev_a2_files = sorted(glob(defs.DEV_LABELS))
    '''
    train_txt_files = sorted(glob(defs.TRAIN_TXT_FILES))
    train_a1_files = sorted(glob(defs.TRAIN_FILES))
    train_a2_files = sorted(glob(defs.TRAIN_LABELS))
    '''
    train_txt_files = sorted(glob(defs.TRAIN_TXT_FILES)+glob(defs.DEV_TXT_FILES))
    train_a1_files = sorted(glob(defs.TRAIN_FILES)+glob(defs.DEV_FILES))
    train_a2_files = sorted(glob(defs.TRAIN_LABELS)+glob(defs.DEV_LABELS))

    test_txt_files = sorted(glob(defs.TEST_TXT_FILES))
    test_a1_files = sorted(glob(defs.TEST_FILES))

    context_embedder = ContextEmbedding()
    if load_file_path is not None:
        print("Loading biotopes dictionary...")
        biotopes = utility.load_pkl(load_file_path)
        print("Successfully loaded.")
    else:
        biotopes = context_parser.find_all_biotope_contexts(train_a1_files, train_a2_files, train_txt_files,
                                                            defs.ONTOBIOTOPE_FILE_PATH)
        print("Creating embeddings for biotopes...")
        biotopes = context_embedder.biotope_embed(biotopes)
        if save_file_path is not None:
            print("Saving biotopes dictionary...")
            utility.save_pkl(biotopes, save_file_path)
            print("Done.")

    e_m = ExactMatch(biotopes)

    with tqdm(total=len(test_a1_files)) as pbar:
        for i in range(len(test_a1_files)):
            biotope_contexts = context_parser.find_a1_file_context(test_a1_files[i], test_txt_files[i])
            matched_terms = {}
            for biotope in biotope_contexts:
                matched_term_list = []
                for bio_context in biotope_contexts[biotope]:
                    #if bio_context.type.microorganism : continue
                    matched_term = context_match_term(biotope, bio_context, biotopes, context_embedder, e_m)
                    matched_term_list.append(matched_term)
                matched_terms[biotope] = [
                    {"id": i.id, "ref": matched_term_list[idx], "type": "N" if i.type == EntityType.microorganism else "O"} for idx, i in
                    enumerate(biotope_contexts[biotope])]

            pbar.update(1)
            bb_normalizer.create_eval_file_for_context(matched_terms, test_a1_files[i])

    print("Updating embeddings for biotopes...")
    biotopes = context_embedder.update_biotope_embed(biotopes)
    if save_file_path is not None:
        print("Saving biotopes dictionary...")
        utility.save_pkl(biotopes, save_file_path)
        print("Done.")



def run_exact_match():
    biotopes = bb_parser.parse_ontobiotope_file(defs.ONTOBIOTOPE_FILE_PATH)
    dev_files = sorted(glob(defs.DEV_FILES))
    dev_labels = sorted(glob(defs.DEV_LABELS))
    exact_match = ExactMatch(biotopes)
    all_entities, all_labels = bb_parser.parse_all_bb_norm_files(dev_files, dev_labels)
    preds_w = exact_match.match_all(all_entities, weighted=True)
    preds = exact_match.match_all(all_entities, weighted=False)
    bb_normalizer.create_eval_file(preds_w, dev_files)
    '''
        import entity
        for i, labels in enumerate(all_labels):
        for j, label in enumerate(labels):
        if all_entities[i][j].type == entity.EntityType.habitat:
        print(f'term:{all_entities[i][j].name}')
        print(f'true:{biotopes[label].name}')
        print(f'pred_w:{biotopes[preds_w[i][j].get("ref","")].name}')
        print(f'pred:{biotopes[preds[i][j].get("ref","")].name}')
    '''


# Check if this file is called directly
if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 1 and _argv_len % 2 == 0:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    _save_file_path = None
    _load_file_path = None

    # Parse the arguments
    for _i in range(1, _argv_len, 2):
        if sys.argv[_i] == '-s':
            _save_file_path = sys.argv[_i + 1]
        elif sys.argv[_i] == '-l':
            _load_file_path = sys.argv[_i + 1]
        else:
            print(f'Unknown option, {sys.argv[_i]}')
            exit(-1)
    # Run the program with given arguments
    # run(_save_file_path, _load_file_path)
    run_exact_match()