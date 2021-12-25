import os

from requirement_file_checks import xml_format_checker


def test_xml_format_when_correct_input():
    path = os.path.join(
        os.path.dirname(__file__), "testdata", "xml_format_correct_input.log"
    )
    checker = xml_format_checker.XmlFormatChecker([path])

    checker.check()

    assert not checker.results


def test_xml_format_when_incorrect_input():
    path = os.path.join(
        os.path.dirname(__file__), "testdata", "xml_format_incorrect_input.log"
    )
    checker = xml_format_checker.XmlFormatChecker([path])

    checker.check()

    assert checker.results
