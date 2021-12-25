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


class BaseChecker:
    def __init__(self, print_prefix: str, filenames: List[str]):
        self.filenames = filenames
        self.print_prefix = print_prefix
        self.results = []

    def check(self):
        for filename in self.filenames:
            self._check(filename)

    def _check(self, filename: str):
        raise NotImplementedError

    def report(self):
        for result in self.results:
            print(f"{self.print_prefix}: {result}")
