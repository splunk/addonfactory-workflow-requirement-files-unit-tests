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
