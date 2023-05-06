from pathlib import Path

import pytest

from ..testings import get_testfile


@pytest.fixture()
def uml_helloworld():
    return get_testfile('umls', 'helloworld.puml')


@pytest.fixture()
def uml_helloworld_code(uml_helloworld):
    return Path(uml_helloworld).read_text()
