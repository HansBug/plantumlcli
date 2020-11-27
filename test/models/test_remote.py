import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from urlobject import URLObject

from plantumlcli.models.remote import OFFICIAL_PLANTUML_HOST, RemotePlantuml
from plantumlcli.utils import all_func
from ..test import exist_func, mark_select, unittest, DEMO_HELLOWORLD_PUML, is_file_func


def _get_test_class(host: str):
    _common_condition = exist_func(host)
    _helloworld_condition = all_func(_common_condition, is_file_func(DEMO_HELLOWORLD_PUML))

    # noinspection DuplicatedCode
    class _TestModelsRemote:
        @classmethod
        def _get_plantuml(cls, host_addr: str) -> RemotePlantuml:
            return RemotePlantuml(host_addr)

        @classmethod
        def _get_auto_plantuml(cls) -> RemotePlantuml:
            return RemotePlantuml.autoload(host=host)

        @mark_select(_common_condition)
        def test_init(self):
            plantuml = self._get_plantuml(host)
            assert plantuml.host == host

        @mark_select(_common_condition)
        def test_init_invalid(self):
            with pytest.raises(ValueError):
                self._get_plantuml('')
            with pytest.raises(ValueError):
                self._get_plantuml(str(URLObject(host).with_scheme('socks5')))

        @mark_select(_common_condition)
        def test_check(self):
            plantuml = self._get_auto_plantuml()
            assert plantuml.test()
            plantuml.check()

        @unittest
        def test_check_invalid(self):
            plantuml = self._get_plantuml('https://www.baidu.com')
            assert not plantuml.test()
            with pytest.raises(ValueError):
                plantuml.check()

        @mark_select(_common_condition)
        def test_repr(self):
            plantuml = self._get_auto_plantuml()
            assert repr(plantuml) == '<RemotePlantuml host: {host}>'.format(host=repr(OFFICIAL_PLANTUML_HOST))

        @mark_select(_helloworld_condition)
        def test_homepage_url(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            assert plantuml.get_homepage_url(
                code) == 'http://www.plantuml.com/plantuml/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

            plantuml2 = self._get_plantuml('https://demo-host-for-plantuml')
            assert plantuml2.get_homepage_url(
                code) == 'https://demo-host-for-plantuml/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        @mark_select(_helloworld_condition)
        def test_url(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()

            assert plantuml.get_url('png', code) \
                   == 'http://www.plantuml.com/plantuml/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
            assert plantuml.get_url('txt', code) \
                   == 'http://www.plantuml.com/plantuml/txt/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
            assert plantuml.get_url('svg', code) \
                   == 'http://www.plantuml.com/plantuml/svg/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
            assert plantuml.get_url('eps', code) \
                   == 'http://www.plantuml.com/plantuml/eps/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

            plantuml2 = self._get_plantuml('https://demo-host-for-plantuml')

            assert plantuml2.get_url('png', code) \
                   == 'https://demo-host-for-plantuml/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
            assert plantuml2.get_url('txt', code) \
                   == 'https://demo-host-for-plantuml/txt/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
            assert plantuml2.get_url('svg', code) \
                   == 'https://demo-host-for-plantuml/svg/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
            assert plantuml2.get_url('eps', code) \
                   == 'https://demo-host-for-plantuml/eps/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        _EXPECTED_TXT_LENGTH_FOR_HELLOWORLD_STR = 224

        @mark_select(_helloworld_condition)
        def test_dump_txt(self):
            plantuml = self._get_auto_plantuml()
            code = Path(DEMO_HELLOWORLD_PUML).read_text()
            txt_result = plantuml.dump_txt(code)

            assert 'Bob' in txt_result
            assert 'Alice' in txt_result
            assert 'hello' in txt_result

            assert self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD_STR * 0.8 < len(
                txt_result) < self._EXPECTED_TXT_LENGTH_FOR_HELLOWORLD_STR * 1.2

        _EXPECTED_TXT_LENGTH_FOR_HELLOWORLD = 372
        _EXPECTED_PNG_LENGTH_FOR_HELLOWORLD = 3020
        _EXPECTED_SVG_LENGTH_FOR_HELLOWORLD = 2742
        _EXPECTED_EPS_LENGTH_FOR_HELLOWORLD = 11048

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

    return _TestModelsRemote


class TestModelsRemoteDefault(_get_test_class(OFFICIAL_PLANTUML_HOST)):
    pass


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
