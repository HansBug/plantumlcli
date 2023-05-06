import os

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
