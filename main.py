import sys
from glob import glob

import context_parser
import defs


def run():
    text = "This is good. This is bad"

    txt_files = sorted(glob(defs.DEV_TXT_FILES))

    list = context_parser.parse_txt_file(txt_files[0])
    tags = context_parser.tag_sentence(list[0])
    unnecessary = None
    

# Check if this file is called directly
if __name__ == "__main__":
    _argv_len = len(sys.argv)

    if _argv_len < 1:
        print(f'Incorrect number of arguments supplied, please check README.md')
        exit(-1)

    # Run the program with given arguments
    run()
