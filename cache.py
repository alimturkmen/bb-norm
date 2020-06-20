import sys

from tqdm import tqdm

import defs
from context_embedding import ContextEmbedding
from context_parser import find_all_biotope_contexts, find_a1_file_context
from entity import DataSet, EmbedCache, BiotopeCache
from utility import save_pkl
import tensorflow as tf


def run(save_dir):
    train_set = DataSet(defs.TRAIN_PATH)
    dev_set = DataSet(defs.DEV_PATH)
    test_set = DataSet(defs.TEST_PATH)

    context_embedding = ContextEmbedding()

    # Structures as follows Dict[file_name, Dict[search_entity.id, EmbedCache]]
    sentence_embeds = {}
    name_embeds = {}
    # Structures as follows Dict[term_id, BiotopeCache]
    biotope_embeds = {}

    # data_set_txt = train_set.txt_files + dev_set.txt_files
    # data_set_a1 = train_set.a1_files + dev_set.a1_files
    # data_set_a2 = train_set.a2_files + dev_set.a2_files

    with tqdm(total=len(test_set.a1_files)) as pbar:
        for i in range(len(test_set.a1_files)):
            file_name = test_set.a1_files[i].split('/')[-1][0:-3]

            sentence_embeds[file_name] = {}
            name_embeds[file_name] = {}

            search_entities_context = find_a1_file_context(test_set.a1_files[i], test_set.txt_files[i])

            for search_entity_context_key in search_entities_context:
                name_embed_cache = EmbedCache(context_embedding.name_embed(search_entity_context_key))

                for search_entity in search_entities_context[search_entity_context_key]:
                    sentence_embed_cache = EmbedCache(
                        tf.convert_to_tensor(context_embedding.sentence_embed([search_entity.sentence]))
                    )

                    name_embeds[file_name][search_entity.id] = name_embed_cache
                    sentence_embeds[file_name][search_entity.id] = sentence_embed_cache

            pbar.update(1)

    # biotopes_contexts = find_all_biotope_contexts(data_set_a1, data_set_a2, data_set_txt,
    #                                               defs.ONTOBIOTOPE_FILE_PATH)
    # biotopes_contexts = context_embedding.biotope_embed(biotopes_contexts)
    #
    # save_pkl(biotopes_contexts, save_dir + "biotope_contexts.pkl")
    #
    # for key in biotopes_contexts:
    #     if biotopes_contexts[key].context_embedding is not None:
    #         context_embed_cache = EmbedCache(biotopes_contexts[key].context_embedding)
    #     else:
    #         context_embed_cache = None
    #
    #     if biotopes_contexts[key].surface_embedding is not None:
    #         surface_embed_cache = EmbedCache(biotopes_contexts[key].surface_embedding)
    #     else:
    #         surface_embed_cache = None
    #
    #     if biotopes_contexts[key].name_embedding is not None:
    #         name_embed_cache = EmbedCache(biotopes_contexts[key].name_embedding)
    #     else:
    #         name_embed_cache = None
    #
    #     biotope_embeds[key] = BiotopeCache(biotopes_contexts[key].name, context_embed_cache,
    #                                        surface_embed_cache,
    #                                        name_embed_cache)

    save_pkl(sentence_embeds, save_dir + "test_sentence_embeds.pkl")
    save_pkl(name_embeds, save_dir + "test_name_embeds.pkl")
    # save_pkl(biotope_embeds, save_dir + "biotope_embeds.pkl")


if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 3:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    _save_dir = None

    # Parse the arguments
    for _i in range(1, _argv_len, 2):
        if sys.argv[_i] == '-s':
            _save_dir = sys.argv[_i + 1]
        else:
            print(f'Unknown option, {sys.argv[_i]}')
            exit(-1)

    run(_save_dir)
