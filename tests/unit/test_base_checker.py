import os
import tempfile

from requirement_file_checks import base_checker


def test_collect_filenames_when_no_files():
    with tempfile.TemporaryDirectory() as tempdir:
        assert not base_checker.collect_filenames(tempdir)


def test_collect_filenames_when_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, "1.log"), "w") as f:
            f.write("content 1")
        os.mkdir(os.path.join(tempdir, "folder"))
        with open(os.path.join(tempdir, "folder", "2.log"), "w") as f:
            f.write("content 2")

        expected_result = [
            os.path.join(tempdir, "1.log"),
            os.path.join(tempdir, "folder", "2.log"),
        ]
        assert expected_result == base_checker.collect_filenames(tempdir)
