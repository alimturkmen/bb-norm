import sys
import glob
import defs
import bb_parser
from bb_normalizer import ExactMatch


def run():
    biotopes = bb_parser.parse_ontobiotope_file(defs.ONTOBIOTOPE_FILE_PATH)

    dev_files = glob.glob(defs.DEV_FILES)
    dev_labels = glob.glob(defs.DEV_LABELS)
    exact_match = ExactMatch(biotopes)

    all_entities, all_labels = bb_parser.parse_all_bb_norm_files(dev_files, dev_labels)
    preds = exact_match.match_all(all_entities)

    unnecessary = None
    

# Check if this file is called directly
if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 1:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    # Run the program with given arguments
    run()
