#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from typing import List
from xml.etree import cElementTree as ET

from base_checker import BaseChecker


class TransportAttributesChecker(BaseChecker):
    def __init__(self, filenames: List[str]):
        super().__init__("transport_attributes_checker", filenames)

    def _check(self, filename: str):
        tree = ET.parse(filename)
        root = tree.getroot()
        transport_type_list = [
            "dbx",
            "modinput",
            "Modinput",
            "Mod input",
            "Modular Input",
            "Modular input",
            "modular input",
            "modular_input",
            "Mod Input",
            "windows_input",
            "hec_event",
            "forwarder",
            "file_monitor",
            "scripted_input",
            "scripted input",
            "hec_raw",
        ]
        for i, event in enumerate(root.iter("event"), 1):
            transport_type = _extract_transport_tag(event)
            if transport_type in transport_type_list:
                host, source, source_type = _check_non_empty_params(event)
                if not (host and source and source_type):
                    self.results.append(
                        f"ERROR: Filename:{filename} Event_no:{i} with transport_type: {transport_type} has missing value. "
                        f'host:"{host}" source:"{source}" or sourcetype:"{source_type}"'
                    )


def _extract_transport_tag(event):
    for transport in event.iter("transport"):
        return transport.get("type")


def _check_non_empty_params(event):
    host, source, source_type = "", "", ""
    for transport in event.iter("transport"):
        if transport.get("host"):
            host = transport.get("host")
        if transport.get("source"):
            source = transport.get("source")
        if transport.get("sourcetype"):
            source_type = transport.get("sourcetype")
    return host, source, source_type
