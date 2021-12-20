#   ########################################################################
#   Copyright 2021 Splunk Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#   #######################################################################
import argparse
import logging
import os
import sys

import lxml
from lxml import etree

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
output_file_handler = logging.FileHandler("test_validation_output.txt", mode="w")
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)
INVALID = False


def validate_input(filename_xml, schema_file):
    xmlschema_doc = etree.parse(schema_file)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    try:
        doc = etree.parse(filename_xml)
    # check for file IO error
    except OSError:
        print("Invalid File")
    except etree.XMLSyntaxError:
        print("XML Syntax Error")
        quit()
    try:
        xmlschema.assertValid(doc)
    except lxml.etree.DocumentInvalid:
        global INVALID
        INVALID = True
        logger.debug("Filename:" + str(filename_xml))
        for error in xmlschema.error_log:
            logger.debug(f"  Line {error.line}: {error.message}")
    # valid = xmlschema.validate(doc)
    # if not valid:
    #     global INVALID
    #     INVALID = True
    #     logger.debug("Filename:" + str(filename_xml))
    #     try:
    #         xmlschema.assert_(doc)
    #     except AssertionError as msg:
    #         logger.debug("Issue:" + str(msg)+'\n')


def parse_input(input_arg, schema_arg):
    if os.path.exists(input_arg):
        if os.path.isfile(input_arg):
            validate_input(input_arg, schema_arg)
        elif os.path.isdir(input_arg):
            for subdir, _, files in os.walk(input_arg):
                for file in files:
                    if file.endswith(".log"):
                        filename = os.path.join(subdir, file)
                        validate_input(filename, schema_arg)
    else:
        logger.debug("Invalid input path")
    if not INVALID:
        logger.debug("No Validation issues in the input file/files in input folder")
    if INVALID:
        exit(1)


if __name__ == "__main__":
    print("Running XML Validation:")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="Input-file/folder to validate against schema",
        required=True,
    )
    parser.add_argument(
        "-s", "--schema_file", help="Schema.xsd location", required=True
    )
    args = parser.parse_args()
    parse_input(args.input, args.schema_file)
