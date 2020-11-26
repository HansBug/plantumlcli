import os
from typing import Optional

import pytest
import where

from plantumlcli import LocalPlantuml
from ..test import PRIMARY_JAR_VERSION, PRIMARY_JAR_PATH, ASSISTANT_JAR_VERSION, ASSISTANT_JAR_PATH, mark_select, \
    DEAD_FILE_PATH


def _get_test_class(version: str, path: str):
    def _common_condition() -> bool:
        return not not (version and path and os.path.exists(path) and where.first('java'))

    def _dead_file_condition() -> bool:
        return not not (_common_condition() and DEAD_FILE_PATH and os.path.exists(DEAD_FILE_PATH))

    class _TestModelsLocal:
        @classmethod
        def _get_plantuml(cls, plantuml: str, java: Optional[str] = None) -> LocalPlantuml:
            return LocalPlantuml(where.first('java') if java is None else java, plantuml)

        @classmethod
        def _get_auto_plantuml(cls) -> LocalPlantuml:
            return LocalPlantuml.autoload(plantuml=path)

        @mark_select(_common_condition)
        def test_version(self):
            plantuml = self._get_auto_plantuml()
            assert version in plantuml.version
            assert 'plantuml' in plantuml.version.lower()

        @mark_select(_common_condition)
        def test_version_error(self):
            with pytest.raises(ValueError):
                _ = self._get_plantuml(java='', plantuml=path)
            with pytest.raises(FileNotFoundError):
                _ = self._get_plantuml(java='path_not_exist', plantuml=path)
            with pytest.raises(IsADirectoryError):
                _ = self._get_plantuml(java=os.path.dirname(path), plantuml=path)

            with pytest.raises(ValueError):
                _ = self._get_plantuml(plantuml='')
            with pytest.raises(FileNotFoundError):
                _ = self._get_plantuml(plantuml='path_not_exist')
            with pytest.raises(IsADirectoryError):
                _ = self._get_plantuml(plantuml=os.path.dirname(path))

        @mark_select(_dead_file_condition)
        def test_version_error_dead(self):
            with pytest.raises(PermissionError):
                _ = self._get_plantuml(java=DEAD_FILE_PATH, plantuml=path)
            with pytest.raises(PermissionError):
                _ = self._get_plantuml(plantuml=DEAD_FILE_PATH)

        @mark_select(_common_condition)
        def test_java(self):
            plantuml = self._get_auto_plantuml()
            assert plantuml.java == where.first('java')

        @mark_select(_common_condition)
        def test_plantuml(self):
            plantuml = self._get_auto_plantuml()
            assert plantuml.plantuml == path

        @mark_select(_common_condition)
        def test_repr(self):
            plantuml = self._get_auto_plantuml()
            assert repr(plantuml) == '<LocalPlantuml java: {java}, plantuml: {plantuml}>'.format(
                java=repr(where.first('java')),
                plantuml=repr(path),
            )

        @mark_select(_common_condition)
        def test_check_and_test(self):
            plantuml = self._get_auto_plantuml()
            plantuml.check()
            assert plantuml.test()

    return _TestModelsLocal


class TestModelsLocalPrimary(_get_test_class(PRIMARY_JAR_VERSION, PRIMARY_JAR_PATH)):
    pass


class TestModelsLocalAssistant(_get_test_class(ASSISTANT_JAR_VERSION, ASSISTANT_JAR_PATH)):
    pass


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
