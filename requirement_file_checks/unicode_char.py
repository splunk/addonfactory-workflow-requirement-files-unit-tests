import re
from typing import List

from base_checker import BaseChecker


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
