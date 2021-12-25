import os

from requirement_file_checks import unicode_char


def test_unicode_char_when_correct_input():
    path = os.path.join(
        os.path.dirname(__file__), "testdata", "unicode_char_correct_input.log"
    )
    checker = unicode_char.UnicodeChecker([path])

    checker.check()

    assert not checker.results


def test_unicode_char_when_incorrect_input():
    path = os.path.join(
        os.path.dirname(__file__), "testdata", "unicode_char_incorrect_input.log"
    )
    checker = unicode_char.UnicodeChecker([path])

    checker.check()

    assert checker.results
