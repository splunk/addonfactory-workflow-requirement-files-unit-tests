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
import os
import sys
import argparse
from lxml import etree
from xml.etree import cElementTree as ET
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
output_file_handler = logging.FileHandler("test_transport_params_output.txt",mode='w')
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)
INVALID = False

#fetches root
def fetch_root_xml(file_name):
    root = None
    try:
        tree = ET.parse(file_name)
        root = tree.getroot()
    except:
        pass
    return root

#fetches transport type
def extract_transport_tag(event):
    for transport in event.iter('transport'):
        return transport.get('type')

#Checks for host source source_type
def check_non_empty_params(event):
    host, source,source_type = "", "",  ""
    for transport in event.iter('transport'):
        if transport.get('host') :
            host = transport.get('host')
        if transport.get('source') :
            source = transport.get('source')
        if transport.get('sourcetype') :
            source_type = transport.get('sourcetype')
    return host, source, source_type

#main transport param function
def check_transport_params(filename):
    try:
        etree.parse(filename)
    # check for file IO error
    except IOError:
        print('Invalid File')
    except etree.XMLSyntaxError:
        print('XML Syntax Error')
        quit()
    root = fetch_root_xml(filename)
    if root is None:
        logger.debug("ERROR parsing xml file" + filename + '\n')
        return
    transport_type_list = ["dbx", "modinput","Modinput", "Mod input","Modular Input", "Modular input", "modular input","modular_input", "Mod Input", "windows_input"]
    event_no = 1
    for event in root.iter('event'):
        transport_type = extract_transport_tag(event)
        if transport_type in transport_type_list:
            host, source, source_type =  check_non_empty_params(event)
            if not( host and source and source_type):
                logger.error(f"ERROR: Filename:{filename} Event_no:{event_no} with transport_type:{transport_type} has missing value.\nhost:\"{host}\" source:\"{source}\" or sourcetype:\"{source_type}\"")
                global INVALID
                INVALID= True
        event_no += 1

#input parsing
def parse_input(input_arg):
    if os.path.exists(input_arg):
        if os.path.isfile(input_arg):
            check_transport_params(input_arg)
        elif os.path.isdir(input_arg):
            for subdir, _, files in os.walk(input_arg):
                for file in files:
                    if file.endswith(".log"):
                        filename = os.path.join(subdir, file)
                        check_transport_params(filename)
    else:
        logger.debug("Invalid input path")
    if not INVALID:
        logger.debug("No Validation issues in the input file/files in input folder")
    if INVALID:
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help='Input-file/folder to test tranport params', required=True)
    args = parser.parse_args()
    parse_input(args.input)
