from typing import List, Dict

import nltk

from bb_parser import parse_bb_a1_file, parse_bb_label_file, parse_ontobiotope_file
from entity import BiotopeContext, Biotope, BiotopeFeatures


def tag_sentence(sentence: str) -> List[tuple]:
    tokens = nltk.word_tokenize(sentence)
    return nltk.pos_tag(tokens)


def parse_txt_file(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read().replace('\n', ' ')

        return parse_sentences(text)


def parse_sentences(text: str) -> List[str]:
    return nltk.sent_tokenize(text, "english")


def find_a1_file_context(a1_path: str, txt_path: str) -> Dict[str, List[BiotopeContext]]:
    entities = parse_bb_a1_file(a1_path)

    sentences = parse_txt_file(txt_path)

    entity_dict = {}

    for entity in entities:
        # Unnecessary check
        annotation_id = entity.id
        if len(entity.name_list) == 0:
            #print("Name list's size is 0\n")
            continue

        sentence_pos = 0
        for sentence in sentences:
            # First check the sentence boundaries. May be the entity occurs multiple time in different sentences.
            # The problem is that, sentence parser omits space at the beginning of the sentence. So some shifts occurs.
            # This may not work at best.
            sentence_pos += len(sentence)
            if sentence_pos - len(sentence) > entity.begin or sentence_pos < entity.begin:
                continue

            # BUG: if name occurs more than once in the sentence, first index will be retrieved. As a solution,
            # sentence length can be compared to entity.begin
            index = sentence.find(entity.name)
            if index == -1:
                continue

            if entity.name in entity_dict:
                entity_dict[entity.name].append(BiotopeContext(annotation_id, sentence, entity.type, index))
            else:
                entity_dict[entity.name] = [BiotopeContext(annotation_id, sentence, entity.type, index)]

            break

    return entity_dict


def find_all_a1_files_contexts(a1_files: List[str], txt_paths: List[str]) -> Dict[str, List[BiotopeContext]]:
    contexts = {}
    for i in range(len(a1_files)):
        biotope_contexts = find_a1_file_context(a1_files[i], txt_paths[i])

        for biotope in biotope_contexts:
            if biotope in contexts:
                contexts[biotope] = contexts[biotope] + biotope_contexts[biotope]
            else:
                contexts[biotope] = biotope_contexts[biotope]

    return contexts


def find_biotope_context(a1_path: str, a2_path: str, txt_path: str) -> Dict[str, BiotopeFeatures] : 

    contexts = find_a1_file_context(a1_path, txt_path)

    labels = parse_bb_label_file(a2_path).entities

    biotope_contexts = {}

    for surface in contexts:
        biocont_list = contexts[surface]
        for biocont in biocont_list:
            annotation_id = biocont.id
            # BUG dev/BB-norm-10496597.a2 file is empty, causes crashing
            biotope_ids = labels[annotation_id]
            sent = biocont.sentence

            for biotope_id in biotope_ids:
                if biotope_id in biotope_contexts:
                    if surface not in biotope_contexts[biotope_id].surfaces:
                        biotope_contexts[biotope_id].add_surface(surface)
                    if sent not in biotope_contexts[biotope_id].sentences:
                        biotope_contexts[biotope_id].add_sentence(sent)
                else:
                    biotope_contexts[biotope_id] = BiotopeFeatures(surface, sent)

    return biotope_contexts


def find_all_biotope_contexts(a1_files: List[str], a2_files:  List[str], txt_paths: List[str], ontobio_file: str) -> Dict[str, Biotope]:
    
    
    biotopes = parse_ontobiotope_file(ontobio_file)
    print("Extracting sentences for biotopes...")

    from tqdm import tqdm
    with tqdm(total=len(a1_files)) as pbar:
        for i in range(len(a1_files)):
            biotope_context = find_biotope_context(a1_files[i], a2_files[i], txt_paths[i])
            
            for biocon in biotope_context:
                if len(biocon) != 6 or biocon[0:2] != '00': continue
                biotopes[biocon].add_context(biotope_context[biocon])
            pbar.update(1)
            

    return biotopes