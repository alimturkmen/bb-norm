from typing import Dict, Any, List

import ijson

import utility
from entity import Biotope


def combine_keys(ontobiotope_terms: Dict[str, Biotope], other_keys: List[Dict[str, Any]]) -> Dict[str, bool]:
    search_keys = {}

    for key in ontobiotope_terms:
        key = ontobiotope_terms[key].name.lower()
        search_keys[key] = False
        for phrase in key.split(' '):
            search_keys[phrase] = False

            for word in phrase.split('-'):
                search_keys[word] = False

    for keys in other_keys:
        for key in keys:
            key = key.lower()
            search_keys[key] = False

            for phrase in key.split(' '):
                search_keys[phrase] = False

                for word in phrase.split('-'):
                    search_keys[word] = False

    return search_keys


def parse_and_filter_w2v(search_keys: Dict[str, Any], w2v_path: str,
                         save_path=None):
    word_embeddings = {}

    vec = [0.0 for i in range(100)]
    generator = ijson.parse(open(w2v_path, 'r', 8192 * 8192))
    try:
        while True:
            prefix, type, key = next(generator)

            if type == 'map_key':
                if key in search_keys:
                    word_embeddings[key] = vec.copy()
                    next(generator)
                    for i in range(100):
                        _, type, value = next(generator)
                        word_embeddings[key][i] = float(value)
                else:
                    for i in range(101):
                        next(generator)

    except StopIteration:
        pass

    if save_path is not None:
        utility.save_pkl(word_embeddings, save_path)
