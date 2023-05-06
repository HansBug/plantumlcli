import os
import shutil
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest

from plantumlcli import LocalPlantuml
from plantumlcli.models.local import LocalPlantumlExecuteError, find_java_from_env, find_java, find_plantuml_from_env, \
    find_plantuml
from test.testings import get_testfile


@pytest.fixture(scope='session')
def java_file():
    return shutil.which('java')


@pytest.fixture()
def broken_jar_file():
    return get_testfile('jars', 'broken.jar')


@pytest.fixture()
def invalid_jar_file():
    return get_testfile('jars', 'helloworld.jar')


@pytest.mark.unittest
class TestModelsLocal:
    @pytest.fixture()
    def plantuml(self, plantuml_jar_file):
        return LocalPlantuml.autoload(plantuml=plantuml_jar_file)

    def test_init_error(self, plantuml_jar_file, java_file):
        with pytest.raises(ValueError):
            _ = LocalPlantuml(java='', plantuml=plantuml_jar_file)
        with pytest.raises(FileNotFoundError):
            _ = LocalPlantuml(java='path_not_exist', plantuml=plantuml_jar_file)
        with pytest.raises(IsADirectoryError):
            _ = LocalPlantuml(java=os.path.dirname(plantuml_jar_file), plantuml=plantuml_jar_file)

        with pytest.raises(ValueError):
            _ = LocalPlantuml(java=java_file, plantuml='')
        with pytest.raises(FileNotFoundError):
            _ = LocalPlantuml(java=java_file, plantuml='path_not_exist')
        with pytest.raises(IsADirectoryError):
            _ = LocalPlantuml(java=java_file, plantuml=os.path.dirname(plantuml_jar_file))

    def test_version(self, plantuml_jar_version, plantuml):
        assert plantuml_jar_version in plantuml.version
        assert 'plantuml' in plantuml.version.lower()

    def test_version_broken(self, plantuml_jar_file, java_file, broken_jar_file):
        plantuml = LocalPlantuml(java=java_file, plantuml=broken_jar_file)
        with pytest.raises(LocalPlantumlExecuteError) as e:
            _ = plantuml.version

        err = e.value
        assert err.exitcode == 1
        assert "invalid or corrupt jarfile" in err.stderr.lower()

    def test_version_invalid(self, plantuml_jar_file, java_file, invalid_jar_file):
        plantuml = LocalPlantuml(java=java_file, plantuml=invalid_jar_file)
        with pytest.raises(ValueError):
            _ = plantuml.version

    def test_java(self, plantuml):
        assert plantuml.java == shutil.which('java')

    def test_plantuml(self, plantuml_jar_file, plantuml):
        assert plantuml.plantuml == plantuml_jar_file

    def test_repr(self, plantuml_jar_file, plantuml):
        assert repr(plantuml) == '<LocalPlantuml java: {java}, plantuml: {plantuml}>'.format(
            java=repr(shutil.which('java')),
            plantuml=repr(plantuml_jar_file),
        )

    def test_check_and_test(self, plantuml):
        plantuml.check()
        assert plantuml.test()

    _EXPECTED_TXT_LENGTH_FOR_HELLOWORLD = 224
    _EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_1 = 2211
    _EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_2 = 3020
    _EXPECTED_SVG_LENGTH_FOR_HELLOWORLD = 2771
    _EXPECTED_EPS_LENGTH_FOR_HELLOWORLD = 11926

    def test_dump_txt(self, uml_helloworld_code, plantuml):
        txt_result = plantuml.dump_txt(uml_helloworld_code)

        assert 'Bob' in txt_result
        assert 'Alice' in txt_result
        assert 'hello' in txt_result

        assert self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 0.8 < len(
            txt_result) < self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 1.2

    def test_dump_binary_txt(self, uml_helloworld_code, plantuml):
        _data = plantuml.dump_binary('txt', uml_helloworld_code)
        assert isinstance(_data, bytes)
        assert self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 0.8 < len(
            _data) < self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 1.2

    def test_dump_binary_png(self, uml_helloworld_code, plantuml):
        _data = plantuml.dump_binary('png', uml_helloworld_code)
        assert isinstance(_data, bytes)
        assert (self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_1 * 0.8 < len(_data) <
                self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_1 * 1.2) or \
               (self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_2 * 0.8 < len(_data) <
                self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_2 * 1.2)

    def test_dump_binary_svg(self, uml_helloworld_code, plantuml):
        _data = plantuml.dump_binary('svg', uml_helloworld_code)
        assert isinstance(_data, bytes)
        assert self._EXPECTED_SVG_LENGTH_FOR_HELLOWORLD * 0.8 < len(
            _data) < self._EXPECTED_SVG_LENGTH_FOR_HELLOWORLD * 1.2

    def test_dump_binary_eps(self, uml_helloworld_code, plantuml):
        _data = plantuml.dump_binary('eps', uml_helloworld_code)
        assert isinstance(_data, bytes)
        assert self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < len(
            _data) < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2

    def test_dump_file_txt(self, uml_helloworld_code, plantuml):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'txt', uml_helloworld_code)
            assert os.path.exists(file.name)
            assert self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize(
                file.name) < self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD * 1.2

    def test_dump_file_png(self, uml_helloworld_code, plantuml):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'png', uml_helloworld_code)
            assert os.path.exists(file.name)
            assert (self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_1 * 0.8 < os.path.getsize(file.name) <
                    self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_1 * 1.2) or \
                   (self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_2 * 0.8 < os.path.getsize(file.name) <
                    self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_2 * 1.2)

    def test_dump_file_svg(self, uml_helloworld_code, plantuml):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'svg', uml_helloworld_code)
            assert os.path.exists(file.name)
            assert self._EXPECTED_SVG_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize(
                file.name) < self._EXPECTED_SVG_LENGTH_FOR_HELLOWORLD * 1.2

    def test_dump_file_eps(self, uml_helloworld_code, plantuml):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'eps', uml_helloworld_code)
            assert os.path.exists(file.name)
            assert self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize(
                file.name) < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2


@pytest.mark.unittest
class TestModelsLocalCommon:
    def test_find_java_from_env(self):
        with patch('shutil.which', lambda x: '/usr/bin/java'):
            assert find_java_from_env() == '/usr/bin/java'
        with patch('shutil.which', lambda x: '/another/java'):
            assert find_java_from_env() == '/another/java'
        with patch('shutil.which', lambda x: ''):
            assert not find_java_from_env()

    def test_find_java(self):
        with patch('shutil.which', lambda x: '/usr/bin/java'):
            assert find_java('/local/java') == '/local/java'
            assert find_java('') == '/usr/bin/java'
        with patch('shutil.which', lambda x: '/another/java'):
            assert find_java('/local/java') == '/local/java'
            assert find_java() == '/another/java'
        with patch('shutil.which', lambda x: ''):
            assert find_java('/local/java') == '/local/java'
            assert not find_java()

    def test_find_plantuml_from_env(self):
        with patch.dict('os.environ', {'PLANTUML_JAR': '/usr/local/plantuml.jar'}):
            assert find_plantuml_from_env() == '/usr/local/plantuml.jar'
        with patch.dict('os.environ', {'PLANTUML_JAR': '/another/plantuml.jar'}):
            assert find_plantuml_from_env() == '/another/plantuml.jar'
        with patch.dict('os.environ', {'PLANTUML_JAR': ''}):
            assert not find_plantuml_from_env()

    def test_find_plantuml(self):
        with patch.dict('os.environ', {'PLANTUML_JAR': '/usr/local/plantuml.jar'}):
            assert find_plantuml('/usr/bin/plantuml.jar') == '/usr/bin/plantuml.jar'
            assert find_plantuml() == '/usr/local/plantuml.jar'
        with patch.dict('os.environ', {'PLANTUML_JAR': '/another/plantuml.jar'}):
            assert find_plantuml('/usr/bin/plantuml.jar') == '/usr/bin/plantuml.jar'
            assert find_plantuml() == '/another/plantuml.jar'
        with patch.dict('os.environ', {'PLANTUML_JAR': ''}):
            assert find_plantuml('/usr/bin/plantuml.jar') == '/usr/bin/plantuml.jar'
            assert not find_plantuml()
