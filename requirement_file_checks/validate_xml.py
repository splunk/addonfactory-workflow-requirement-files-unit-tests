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
import os
from typing import List

import lxml
from lxml import etree

from requirement_file_checks.base_checker import BaseChecker


class XMLChecker(BaseChecker):
    def __init__(self, filenames: List[str]):
        super().__init__("validate_xml", filenames)
        self._schema_file = os.path.join(
            os.path.dirname(__file__),
            "schema.xsd",
        )

    def _check(self, filename: str):
        xmlschema_doc = etree.parse(self._schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        try:
            doc = etree.parse(filename)
            xmlschema.assertValid(doc)
        except lxml.etree.DocumentInvalid:
            for error in xmlschema.error_log:
                self.results.append(f"Line {error.line}: {error.message}")
