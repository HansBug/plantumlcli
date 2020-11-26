import os

import pytest
import where

from plantumlcli import LocalPlantuml
from ..test import PRIMARY_JAR_VERSION, PRIMARY_JAR_PATH, ASSISTANT_JAR_VERSION, ASSISTANT_JAR_PATH, mark_select


def _get_test_class(version: str, path: str):
    @mark_select(lambda: not not (version and path and os.path.exists(path) and where.first('java')))
    class _TestModelsLocal:
        @classmethod
        def _get_plantuml(cls) -> LocalPlantuml:
            return LocalPlantuml(plantuml=path, java=where.first('java'))

        def test_version(self):
            plantuml = self._get_plantuml()
            assert version in plantuml.version
            assert 'plantuml' in plantuml.version.lower()

    return _TestModelsLocal


class TestModelsLocalPrimary(_get_test_class(PRIMARY_JAR_VERSION, PRIMARY_JAR_PATH)):
    pass


class TestModelsLocalAssistant(_get_test_class(ASSISTANT_JAR_VERSION, ASSISTANT_JAR_PATH)):
    pass


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
