import os
import re

import pytest
from huggingface_hub import hf_hub_download


@pytest.fixture(scope='session')
def plantuml_jar_version():
    return os.environ.get('PLANTUML_JAR_VERSION', '1.2020.19')


@pytest.fixture(scope='session')
def plantuml_jar_file(plantuml_jar_version):
    return hf_hub_download(
        'HansBug/opensource_mirror',
        f'plantuml/{plantuml_jar_version}/plantuml.{plantuml_jar_version}.jar',
        repo_type='dataset',
    )


@pytest.fixture(scope='session')
def plantuml_host():
    return os.environ.get('PLANTUML_HOST')


@pytest.fixture(scope='session')
def plantuml_server_version():
    raw = os.environ.get('PLANTUML_SERVER_VERSION')
    if raw:
        (major, year, v), = re.findall(r'v(?P<major>\d+).(?P<year>\d+).(?P<v>\d+)', raw, re.IGNORECASE)
        return int(major), int(year), int(v.lstrip('0') or '0')
    else:
        return None


# this is a buggy version which will cause error in plantumlcli
@pytest.fixture(scope='session')
def skip_for_server_v1202307(plantuml_server_version):
    if plantuml_server_version == (1, 2023, 7):
        pytest.skip('Skipped due to plantuml-server v1.2023.7')
