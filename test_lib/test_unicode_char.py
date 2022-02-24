import argparse
import logging
import os
import re
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
output_file_handler = logging.FileHandler("test_check_unicode_output.txt", mode="w")
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)
INVALID = False


def test_unicode_char(filename):
    global INVALID
    # pattern = re.compile("[^\x00-\x7F]") #do ot want to replace printable chars like €¢ etc
    pattern = re.compile(
        "[\u200B-\u200E\uFEFF\u202c\u202D\u2063\u2062]"
    )  # zero width characters
    for i, line in enumerate(open(filename)):
        for match in re.finditer(pattern, line):
            logger.debug(
                "Unicode char in FILE {} Line {}: {}".format(
                    filename, i + 1, match.group().encode("utf-8")
                )
            )
            INVALID = True


# input parsing
def parse_input(input_arg):
    if os.path.exists(input_arg):
        if os.path.isfile(input_arg):
            test_unicode_char(input_arg)
        elif os.path.isdir(input_arg):
            for subdir, _, files in os.walk(input_arg):
                for file in files:
                    if file.endswith(".log") or file.endswith(".xml"):
                        filename = os.path.join(subdir, file)
                        test_unicode_char(filename)
    else:
        logger.debug("Invalid input path")
    if not INVALID:
        logger.debug("No Unicode chars found")
    if INVALID:
        logger.error(
            "Please open file in terminal or vi to view hidden unicode chars in files"
        )
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="Input-file/folder to test unicode chars", required=True
    )
    args = parser.parse_args()
    parse_input(args.input)
