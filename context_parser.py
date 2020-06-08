from typing import List

import nltk


def tag_sentence(sentence: str) -> List[tuple]:
    tokens = nltk.word_tokenize(sentence)
    return nltk.pos_tag(tokens)


def parse_txt_file(path: str) -> List[str]:
    with open(path, 'r') as f:
        text = f.read().replace('\n', ' ')

        return parse_sentences(text)


def parse_sentences(text: str) -> List[str]:
    return nltk.sent_tokenize(text, "english")
