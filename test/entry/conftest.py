import pytest

from ..testings import get_testfile


@pytest.fixture()
def uml_helloworld():
    return get_testfile('umls', 'helloworld.puml')


@pytest.fixture()
def uml_common():
    return get_testfile('umls', 'common.puml')


@pytest.fixture()
def uml_chinese():
    return get_testfile('umls', 'chinese.puml')


@pytest.fixture()
def uml_invalid():
    return get_testfile('umls', 'invalid.puml')


@pytest.fixture()
def uml_large():
    return get_testfile('umls', 'large.puml')
