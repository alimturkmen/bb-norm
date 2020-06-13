from typing import List, Dict

import nltk

from bb_parser import parse_bb_a1_file
from entity import BiotopeContext


def tag_sentence(sentence: str) -> List[tuple]:
    tokens = nltk.word_tokenize(sentence)
    return nltk.pos_tag(tokens)


def parse_txt_file(path: str) -> List[str]:
    with open(path, 'r') as f:
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
        if len(entity.name_list) == 0:
            print("name list's size is 0\n")
            break

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
                entity_dict[entity.name].append(BiotopeContext(sentence, index))
            else:
                entity_dict[entity.name] = [BiotopeContext(sentence, index)]

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
