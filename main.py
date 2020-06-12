import sys
from glob import glob

import bb_normalizer
import bb_parser
import context_parser
import defs
from bb_normalizer import ExactMatch


def run():
    txt_files = sorted(glob(defs.DEV_TXT_FILES))
    dev_a1_files = sorted(glob(defs.DEV_FILES))

    context = context_parser.find_a1_file_context(dev_a1_files[0], txt_files[0])

    unnecessary = None

def run_exact_match():
    biotopes = bb_parser.parse_ontobiotope_file(defs.ONTOBIOTOPE_FILE_PATH)
    dev_files = sorted(glob.glob(defs.DEV_FILES))
    dev_labels = sorted(glob.glob(defs.DEV_LABELS))
    exact_match = ExactMatch(biotopes)
    all_entities, all_labels = bb_parser.parse_all_bb_norm_files(dev_files, dev_labels)
    preds_w = exact_match.match_all(all_entities, weighted=True)
    preds = exact_match.match_all(all_entities, weighted=False)
    bb_normalizer.create_eval_file(preds_w, dev_files)
    '''
        import entity
        for i, labels in enumerate(all_labels):
        for j, label in enumerate(labels):
        if all_entities[i][j].type == entity.EntityType.habitat:
        print(f'term:{all_entities[i][j].name}')
        print(f'true:{biotopes[label].name}')
        print(f'pred_w:{biotopes[preds_w[i][j].get("ref","")].name}')
        print(f'pred:{biotopes[preds[i][j].get("ref","")].name}')
    '''


# Check if this file is called directly
if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 1:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    # Run the program with given arguments
    run()
