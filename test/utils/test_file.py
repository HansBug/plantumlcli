import os
import tempfile
from pathlib import Path

import pytest

from plantumlcli.utils import save_binary_file, save_text_file, load_binary_file, load_text_file
from ..test import unittest


@unittest
class TestUtilsFile:
    def test_save_binary_file(self):
        with tempfile.NamedTemporaryFile() as fw:
            data = b'kasdjfg980u3904utr89037q0g98hawep09fgjpwe4uf-023if[ojdfhgkjsdhk\x002349'
            save_binary_file(fw.name, data)

            assert Path(fw.name).read_bytes() == data

    def test_save_text_file(self):
        with tempfile.NamedTemporaryFile() as fw:
            text = 'kasdjfg980u3904utr89037q0g98hawep09fgjpwe4uf-023if[ojdfhgkjsdhk\x002349'
            save_text_file(fw.name, text)

            assert Path(fw.name).read_text() == text

    def test_load_binary_file(self):
        with tempfile.NamedTemporaryFile() as fw:
            data = b'kasdjfg980u3904utr89037q0g98hawep09fgjpwe4uf-023if[ojdfhgkjsdhk\x002349'
            Path(fw.name).write_bytes(data)

            assert load_binary_file(fw.name) == data

    def test_load_text_file(self):
        with tempfile.NamedTemporaryFile() as fw:
            text = 'kasdjfg980u3904utr89037q0g98hawep09fgjpwe4uf-023if[ojdfhgkjsdhk\x002349'
            Path(fw.name).write_text(text)

            assert load_text_file(fw.name) == text


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
