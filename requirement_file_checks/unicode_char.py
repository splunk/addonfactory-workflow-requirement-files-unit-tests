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
import re
from typing import List

from requirement_file_checks.base_checker import BaseChecker


class UnicodeChecker(BaseChecker):
    def __init__(self, filenames: List[str]):
        super().__init__("unicode_checker", filenames)

    def _check(self, filename: str):
        pattern = re.compile(
            "[\u200B-\u200E\uFEFF\u202c\u202D\u2063\u2062]"
        )  # zero width characters
        for i, line in enumerate(open(filename), 1):
            for match in re.finditer(pattern, line):
                self.results.append(
                    "Unicode char in line {}: {}".format(
                        i, match.group().encode("utf-8")
                    )
                )
