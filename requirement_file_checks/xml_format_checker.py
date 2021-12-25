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
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

from base_checker import BaseChecker


class XmlFormatChecker(BaseChecker):
    def __init__(self, filenames: List[str]):
        super().__init__("xml_format_checker", filenames)

    def _check(self, filename: str):
        parser = make_parser()
        parser.setContentHandler(ContentHandler())
        try:
            parser.parse(filename)
        except:
            self.results.append(f"Cannot parse {filename} as an XML")
