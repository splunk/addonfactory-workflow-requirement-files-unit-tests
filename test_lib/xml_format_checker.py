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
import logging
import os
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

from common_util import return_folder_contents

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
output_file_handler = logging.FileHandler("test_format_output.txt", mode="w")
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)


def parsefile(file):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(file)


def check_xml_format(input_folder):
    file_list = return_folder_contents(input_folder)
    contains_log, contains_XML, test_status = False, False, True
    for fname in file_list:
        if fname.endswith(".log"):
            contains_log = True
        else:
            contains_XML = True
        try:
            parsefile(fname)
            print(f" Pass : {str(fname)}")
        except Exception as e:
            test_status = False
            logger.debug(str(e) + "\n")
            logging.error(f" Failed : {str(e)}")
        if contains_XML and contains_log:
            logger.error(" Failed: All files should either be .log or .xml extension")
            test_status = False
    return test_status


if __name__ == "__main__":
    print("Running XML format checker:")
    try:
        inputFolder = sys.argv[1]
    except:
        print("Please pass directory_name")
    if len(sys.argv) != 1:
        inputFolder = sys.argv[1]
    test_result = check_xml_format(inputFolder)
    if test_result:
        logger.debug("No formatting errors ")
    else:
        exit(1)
