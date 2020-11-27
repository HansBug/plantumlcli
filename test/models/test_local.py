import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

import pytest
import where

from plantumlcli import LocalPlantuml
from plantumlcli.models.local import LocalPlantumlExecuteError
from plantumlcli.utils import all_func
from ..test import PRIMARY_JAR_VERSION, PRIMARY_JAR_PATH, ASSISTANT_JAR_VERSION, ASSISTANT_JAR_PATH, mark_select, \
    DEAD_FILE_PATH, DEMO_HELLOWORLD_PUML, is_file_func, BROKEN_JAR_PATH, INVALID_JAR_PATH


def _get_test_class(version: str, path: str):
    _common_condition = all_func(lambda: not not (version and path and os.path.exists(path) and where.first('java')))
    _dead_file_condition = all_func(_common_condition, is_file_func(DEAD_FILE_PATH))
    _broken_jar_condition = all_func(_common_condition, is_file_func(BROKEN_JAR_PATH))
    _invalid_jar_condition = all_func(_common_condition, is_file_func(INVALID_JAR_PATH))
    _helloworld_condition = all_func(_common_condition, is_file_func(DEMO_HELLOWORLD_PUML))

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

        @mark_select(_broken_jar_condition)
        def test_version_broken(self):
            plantuml = self._get_plantuml(plantuml=BROKEN_JAR_PATH)
            with pytest.raises(LocalPlantumlExecuteError) as e:
                _ = plantuml.version

            err = e.value
            assert err.exitcode == 1
            assert "invalid or corrupt jarfile" in err.stderr.lower()

        @mark_select(_invalid_jar_condition)
        def test_version_invalid(self):
            plantuml = self._get_plantuml(plantuml=INVALID_JAR_PATH)
            with pytest.raises(ValueError):
                _ = plantuml.version

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

        _EXPECTED_TXT_LENGTH_FOR_HELLOWORLD = 224
        _EXPECTED_PNG_LENGTH_FOR_HELLOWORLD = 2211
        _EXPECTED_SVG_LENGTH_FOR_HELLOWORLD = 2771
        _EXPECTED_EPS_LENGTH_FOR_HELLOWORLD = 11926

        @mark_select(_helloworld_condition)
        def test_dump_txt(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()
            txt_result = plantuml.dump_txt(code)

            assert 'Bob' in txt_result
            assert 'Alice' in txt_result
            assert 'hello' in txt_result

            assert self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 0.8 < len(
                txt_result) < self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 1.2

        @mark_select(_helloworld_condition)
        def test_dump_binary_txt(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            _data = plantuml.dump_binary('txt', code)
            assert isinstance(_data, bytes)
            assert self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 0.8 < len(
                _data) < self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 1.2

        @mark_select(_helloworld_condition)
        def test_dump_binary_png(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            _data = plantuml.dump_binary('png', code)
            assert isinstance(_data, bytes)
            assert self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD * 0.8 < len(
                _data) < self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD * 1.2

        @mark_select(_helloworld_condition)
        def test_dump_binary_svg(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            _data = plantuml.dump_binary('svg', code)
            assert isinstance(_data, bytes)
            assert self._EXPECTED_SVG_LENGTH_FOR_HELLOWORLD * 0.8 < len(
                _data) < self._EXPECTED_SVG_LENGTH_FOR_HELLOWORLD * 1.2

        @mark_select(_helloworld_condition)
        def test_dump_binary_eps(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            _data = plantuml.dump_binary('eps', code)
            assert isinstance(_data, bytes)
            assert self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < len(
                _data) < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2

        @mark_select(_helloworld_condition)
        def test_dump_file_txt(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            with NamedTemporaryFile() as file:
                plantuml.dump(file.name, 'txt', code)
                assert os.path.exists(file.name)
                assert self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize(
                    file.name) < self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 1.2

        @mark_select(_helloworld_condition)
        def test_dump_file_png(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            with NamedTemporaryFile() as file:
                plantuml.dump(file.name, 'png', code)
                assert os.path.exists(file.name)
                assert self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize(
                    file.name) < self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD * 1.2

        @mark_select(_helloworld_condition)
        def test_dump_file_svg(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            with NamedTemporaryFile() as file:
                plantuml.dump(file.name, 'svg', code)
                assert os.path.exists(file.name)
                assert self._EXPECTED_SVG_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize(
                    file.name) < self._EXPECTED_SVG_LENGTH_FOR_HELLOWORLD * 1.2

        @mark_select(_helloworld_condition)
        def test_dump_file_eps(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            with NamedTemporaryFile() as file:
                plantuml.dump(file.name, 'eps', code)
                assert os.path.exists(file.name)
                assert self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize(
                    file.name) < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2

    return _TestModelsLocal


class TestModelsLocalPrimary(_get_test_class(PRIMARY_JAR_VERSION, PRIMARY_JAR_PATH)):
    pass


class TestModelsLocalAssistant(_get_test_class(ASSISTANT_JAR_VERSION, ASSISTANT_JAR_PATH)):
    pass


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
