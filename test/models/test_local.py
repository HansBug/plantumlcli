import os
import shutil
from tempfile import NamedTemporaryFile
from typing import List
from unittest import skipUnless
from unittest.mock import patch

import pytest

from plantumlcli import LocalPlantuml
from plantumlcli.models.local import LocalPlantumlExecuteError, find_java_from_env, find_java, find_plantuml_from_env, \
    find_plantuml
from .conftest import _has_cairosvg
from ..testings import get_testfile


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
        assert repr(plantuml) == \
               f'<LocalPlantuml java: {shutil.which("java")!r}, plantuml: {plantuml_jar_file!r}>'

    def test_check_and_test(self, plantuml):
        plantuml.check()
        assert plantuml.test()

    _TXT_SIZES = [224, 372]
    _PNG_SIZES = [3020, 2211]
    _SVG_SIZES = [2771, 2003]
    _EPS_SIZES = [11926, 7938]
    _PDF_SIZES = [1811] if not _has_cairosvg() else [6326]

    @classmethod
    def _size_check(cls, expected_sizes: List[int], size: int):
        ranges = [(int(0.8 * exp_size), int(1.2 * exp_size)) for exp_size in expected_sizes]
        assert any(lbound <= size <= rbound for lbound, rbound in ranges), \
            f'Size in range {ranges!r} expected, but {size!r} found.'

    def test_dump_txt(self, uml_helloworld_code, plantuml):
        txt_result = plantuml.dump_txt(uml_helloworld_code)

        assert 'Bob' in txt_result
        assert 'Alice' in txt_result
        assert 'hello' in txt_result

        self._size_check(self._TXT_SIZES, len(txt_result))

    def test_dump_binary_txt(self, uml_helloworld_code, plantuml):
        _data = plantuml.dump_binary('txt', uml_helloworld_code)
        assert isinstance(_data, bytes)
        self._size_check(self._TXT_SIZES, len(_data))

    def test_dump_binary_png(self, uml_helloworld_code, plantuml):
        _data = plantuml.dump_binary('png', uml_helloworld_code)
        assert isinstance(_data, bytes)
        self._size_check(self._PNG_SIZES, len(_data))

    def test_dump_binary_svg(self, uml_helloworld_code, plantuml):
        _data = plantuml.dump_binary('svg', uml_helloworld_code)
        assert isinstance(_data, bytes)
        self._size_check(self._SVG_SIZES, len(_data))

    def test_dump_binary_eps(self, uml_helloworld_code, plantuml):
        _data = plantuml.dump_binary('eps', uml_helloworld_code)
        assert isinstance(_data, bytes)
        self._size_check(self._EPS_SIZES, len(_data))

    @skipUnless(_has_cairosvg(), 'Cairosvg required.')
    def test_dump_binary_pdf(self, uml_helloworld_code, plantuml):
        _data = plantuml.dump_binary('pdf', uml_helloworld_code)
        assert isinstance(_data, bytes)
        self._size_check(self._PDF_SIZES, len(_data))

    def test_dump_file_txt(self, uml_helloworld_code, plantuml):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'txt', uml_helloworld_code)
            assert os.path.exists(file.name)
            self._size_check(self._TXT_SIZES, os.path.getsize(file.name))

    def test_dump_file_png(self, uml_helloworld_code, plantuml):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'png', uml_helloworld_code)
            assert os.path.exists(file.name)
            self._size_check(self._PNG_SIZES, os.path.getsize(file.name))

    def test_dump_file_svg(self, uml_helloworld_code, plantuml):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'svg', uml_helloworld_code)
            assert os.path.exists(file.name)
            self._size_check(self._SVG_SIZES, os.path.getsize(file.name))

    def test_dump_file_eps(self, uml_helloworld_code, plantuml):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'eps', uml_helloworld_code)
            assert os.path.exists(file.name)
            self._size_check(self._EPS_SIZES, os.path.getsize(file.name))

    @skipUnless(_has_cairosvg(), 'Cairosvg required.')
    def test_dump_file_pdf(self, uml_helloworld_code, plantuml):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'pdf', uml_helloworld_code)
            assert os.path.exists(file.name)
            self._size_check(self._PDF_SIZES, os.path.getsize(file.name))


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
