import os

from requirement_file_checks import transport_attrib


def test_transport_attribute_when_correct_input():
    path = os.path.join(
        os.path.dirname(__file__), "testdata", "transport_attrib_correct_input.log"
    )
    checker = transport_attrib.TransportAttributesChecker([path])

    checker.check()

    assert not checker.results


def test_transport_attribute_when_incorrect_input():
    path = os.path.join(
        os.path.dirname(__file__), "testdata", "transport_attrib_incorrect_input.log"
    )
    checker = transport_attrib.TransportAttributesChecker([path])

    checker.check()

    assert checker.results
