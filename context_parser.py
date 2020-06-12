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

            index = sentence.find(entity.name)
            if index == -1:
                continue

            if entity.name in entity_dict:
                entity_dict[entity.name].append(BiotopeContext(sentence, index))
            else:
                entity_dict[entity.name] = [BiotopeContext(sentence, index)]

            break

    return entity_dict
