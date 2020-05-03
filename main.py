import sys
import defs
import parser


def run():
    biotopes = parser.parse_ontobiotope_file(defs.ONTOBIOTOPE_FILE_PATH)

    search_entities = parser.parse_bb_norm_file(defs.DEV_FILE)

    unnecessary = None


# Check if this file is called directly
if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 1:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    # Run the program with given arguments
    run()
