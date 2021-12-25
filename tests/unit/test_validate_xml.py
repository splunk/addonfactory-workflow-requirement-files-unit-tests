import os

from requirement_file_checks import validate_xml


def test_validate_xml_when_correct_input():
    path = os.path.join(
        os.path.dirname(__file__), "testdata", "validate_xml_correct_input.log"
    )
    checker = validate_xml.XMLChecker([path])

    checker.check()

    assert not checker.results


def test_validate_xml_when_incorrect_input():
    path = os.path.join(
        os.path.dirname(__file__), "testdata", "validate_xml_incorrect_input.log"
    )
    checker = validate_xml.XMLChecker([path])

    checker.check()

    assert checker.results
