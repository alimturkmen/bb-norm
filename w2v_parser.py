#! /usr/bin/env python
import sys
from typing import Dict, Any, List

import ijson

import defs
import utility
from bb_parser import parse_ontobiotope_file
from context_parser import find_all_a1_files_contexts
from entity import Biotope, DataSet


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


def run(save_path: str, w2v_path: str):
    ontobiotope_terms = parse_ontobiotope_file(defs.ONTOBIOTOPE_FILE_PATH)
    dev_set = DataSet(defs.DEV_PATH)
    test_set = DataSet(defs.TEST_PATH)
    train_set = DataSet(defs.TRAIN_PATH)

    dev_a1_context = find_all_a1_files_contexts(dev_set.a1_files, dev_set.txt_files)
    test_a1_context = find_all_a1_files_contexts(test_set.a1_files, test_set.txt_files)
    train_a1_context = find_all_a1_files_contexts(train_set.a1_files, train_set.txt_files)

    parse_and_filter_w2v(
        combine_keys(ontobiotope_terms, [dev_a1_context, test_a1_context, train_a1_context]),
        w2v_path,
        save_path)


if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 3:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    _w2v_path = sys.argv[1]
    _save_file_path = sys.argv[2]

    # Run the program with given arguments
    run(_save_file_path, _w2v_path)
