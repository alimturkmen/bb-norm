from typing import List

import defs
from entity import Prediction


def create_predictions_evaluate_file(predictions: List[Prediction], file_path: str):
    file_name = file_path.split('/')[-1][0:-3] + '.a2'
    with open(defs.OUTPUT_PATH + file_name, 'w') as file:
        for (i, prediction) in enumerate(predictions):
            line = "N{}\t".format(str(i)) + prediction.print() + "\n"
            file.write(line)
