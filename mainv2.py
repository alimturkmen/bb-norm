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


def run(load_dir):
    test_set = DataSet(defs.TEST_PATH)

    (se_sentences_embeds, se_name_embed, biotope_embeds, biotopes) = load_cache(load_dir)

    exact_match_predictor = ExactMatch(biotopes)

    total_search_entity = 0
    context_predicted_entity = 0
    exact_predicted_entity = 0
    interval = "1"
    with tqdm(total=len(test_set.a1_files)) as pbar:
        for path in test_set.a1_files:
            file_name = path.split('\\')[-1][0:-3] #BUG

            search_entities = parse_bb_a1_file(path)

            predictions = []

            print("Current File {}".format(file_name))

            for search_entity in search_entities:
                
                # if not in the dict, it must have some invalid character
                if search_entity.id not in se_sentences_embeds[
                    file_name] or search_entity.type == EntityType.microorganism:
                    predictions.append(Prediction(search_entity.id, "000000", search_entity.type, 0))
                    continue

                predicted_term = context_predictor(search_entity, se_sentences_embeds[file_name][search_entity.id],
                                                   se_name_embed[file_name][search_entity.id], biotope_embeds)

                if predicted_term.confidence < 0.60:
                    exact_match = exact_match_predictor.weighted_match_term(search_entity)
                    if exact_match['score'] < 1.0: 
                        total_search_entity += 1
                        continue
                    predicted_term = Prediction(search_entity.id, exact_match["ref"], search_entity.type,
                                                exact_match["score"])
                    exact_predicted_entity += 1
                else:
                    context_predicted_entity += 1

                predictions.append(predicted_term)

                total_search_entity += 1

            create_predictions_evaluate_file(predictions, path)
            pbar.update(1)

    with open("../outputs/statistics/run-" + interval, "w") as file:
        file.write("total predicted: {}, exact_predicted: {}, context_predictd: {}"
                   .format(str(total_search_entity), str(exact_predicted_entity), str(context_predicted_entity))
                   )


if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 3:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    _load_dir = None

    # Parse the arguments
    for _i in range(1, _argv_len, 2):
        if sys.argv[_i] == '-l':
            _load_dir = sys.argv[_i + 1]
        else:
            print(f'Unknown option, {sys.argv[_i]}')
            exit(-1)
    # Run the program with given arguments
    run(_load_dir)
