#! /usr/bin/env python
import sys

from tqdm import tqdm

import defs
from bb_normalizer import ExactMatch
from bb_parser import parse_bb_a1_file
from entity import DataSet, Prediction, EntityType
from evaluators import create_predictions_evaluate_file
from predictors import context_predictor
from utility import load_pkl


def load_cache(load_dir):
    return load_pkl(
        load_dir + "test_sentence_embeds.pkl"), load_pkl(load_dir + "test_name_embeds.pkl"), load_pkl(
        load_dir + "biotope_embeds.pkl"), load_pkl(load_dir + "biotope_contexts.pkl")


def run(load_dir: str, start_index: int, length: int):
    test_set = DataSet(defs.TEST_PATH)

    (se_sentences_embeds, se_name_embed, biotope_embeds, biotopes) = load_cache(load_dir)

    exact_match_predictor = ExactMatch(biotopes)

    with tqdm(total=len(test_set.a1_files[start_index:start_index + length])) as pbar:
        for path in test_set.a1_files[start_index:start_index + length]:
            file_name = path.split('/')[-1][0:-3]

            search_entities = parse_bb_a1_file(path)

            predictions = []

            print("Current File {}".format(file_name))

            for search_entity in search_entities:
                # if not in the dict, it must have some invalid character
                if search_entity.id not in se_sentences_embeds[file_name] or \
                        search_entity.type == EntityType.microorganism:
                    predictions.append(Prediction(search_entity.id, "000000", search_entity.type, 0))
                    continue

                predicted_term = context_predictor(search_entity, se_sentences_embeds[file_name][search_entity.id],
                                                   se_name_embed[file_name][search_entity.id], biotope_embeds)

                if predicted_term.confidence < 0.55:
                    exact_match = exact_match_predictor.weighted_match_term(search_entity)
                    predicted_term = Prediction(search_entity.id, exact_match["ref"], search_entity.type,
                                                exact_match["score"])
                    if predicted_term.confidence == 0:
                        continue

                predictions.append(predicted_term)

            create_predictions_evaluate_file(predictions, path)
            pbar.update(1)


if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 3:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    _load_dir = sys.argv[1]
    _start_index = sys.argv[2]
    _length = sys.argv[3]

    # Run the program with given arguments
    run(_load_dir, int(_start_index), int(_length))
