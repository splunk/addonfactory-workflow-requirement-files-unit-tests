import argparse
import os
from typing import List

from cim import CimChecker
from transport_attrib import TransportAttributesChecker
from unicode_char import UnicodeChecker
from validate_xml import XMLChecker
from xml_format_checker import XmlFormatChecker


def _collect_filenames(path: str) -> List[str]:
    filenames = []
    if os.path.exists(path):
        if os.path.isfile(path):
            filenames.append(path)
        elif os.path.isdir(path):
            for subdir, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".log"):
                        filename = os.path.join(subdir, file)
                        filenames.append(filename)
    return filenames


def run(path: str):
    filenames = _collect_filenames(path)
    print(f"Collected filenames: {filenames}")
    if not filenames:
        raise SystemExit("No files to check")
    xml_format_checker = XmlFormatChecker(filenames)
    xml_format_checker.check()
    if xml_format_checker.results:
        xml_format_checker.report()
        raise SystemExit("Fix XML format first")
    checkers = [
        XMLChecker(filenames),
        TransportAttributesChecker(filenames),
        UnicodeChecker(filenames),
        CimChecker(filenames),
    ]
    failure = False
    for checker in checkers:
        checker.check()
        if checker.results:
            failure = True
        checker.report()
    if failure:
        raise SystemExit("Some of the checkers failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="Input-file/folder to test transport params",
        required=True,
    )
    args = parser.parse_args()
    run(args.input)
