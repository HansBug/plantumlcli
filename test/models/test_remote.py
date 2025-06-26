import os
from tempfile import NamedTemporaryFile
from typing import Optional, List
from unittest.mock import patch

import pytest
from urlobject import URLObject

from plantumlcli.models.remote import OFFICIAL_PLANTUML_HOST, RemotePlantuml, find_plantuml_host_from_env, \
    find_plantuml_host
from .conftest import _has_cairosvg


@pytest.mark.unittest
@pytest.mark.parametrize(['is_official'], [(True,), (False,)])
class TestModelsRemote:
    @pytest.fixture()
    def host(self, is_official, plantuml_host):
        host_addr = OFFICIAL_PLANTUML_HOST if is_official else plantuml_host
        if not host_addr:
            pytest.skip('No plantuml host assigned')
            return None
        else:
            return host_addr

    @pytest.fixture()
    def plantuml(self, host):
        return RemotePlantuml.autoload(host=host)

    def test_init(self, host):
        plantuml = RemotePlantuml(host)
        assert plantuml.host == host

    def test_init_invalid(self, host):
        with pytest.raises(ValueError):
            RemotePlantuml('')
        with pytest.raises(ValueError):
            RemotePlantuml(str(URLObject(host).with_scheme('socks5')))

    def test_check(self, plantuml):
        assert plantuml.test()
        plantuml.check()

    def test_check_invalid(self, is_official):
        _ = is_official
        plantuml = RemotePlantuml('https://www.baidu.com')
        assert not plantuml.test()
        with pytest.raises(ValueError):
            plantuml.check()

    def test_repr(self, host, plantuml):
        assert repr(plantuml) == f'<RemotePlantuml host: {host!r}>'

    def test_homepage_url(self, plantuml, uml_helloworld, uml_helloworld_code, host):
        def _append_path(path: str, host_addr: Optional[str] = None) -> str:
            return str(URLObject(host_addr or host).without_query().without_fragment().add_path(path))

        assert plantuml.get_homepage_url(
            uml_helloworld_code) == _append_path('uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80')

        plantuml2 = RemotePlantuml('https://demo-host-for-plantuml')
        assert plantuml2.get_homepage_url(
            uml_helloworld_code) == _append_path('uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80',
                                                 'https://demo-host-for-plantuml')

    def test_url(self, plantuml, uml_helloworld, uml_helloworld_code, host):
        def _append_path(path: str, host_addr: Optional[str] = None) -> str:
            return str(URLObject(host_addr or host).without_query().without_fragment().add_path(path))

        assert plantuml.get_url('png', uml_helloworld_code) \
               == _append_path('png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80')
        assert plantuml.get_url('txt', uml_helloworld_code) \
               == _append_path('txt/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80')
        assert plantuml.get_url('svg', uml_helloworld_code) \
               == _append_path('svg/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80')
        assert plantuml.get_url('eps', uml_helloworld_code) \
               == _append_path('eps/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80')

        plantuml2 = RemotePlantuml('https://demo-host-for-plantuml')

        assert plantuml2.get_url('png', uml_helloworld_code) \
               == _append_path('png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80',
                               'https://demo-host-for-plantuml')
        assert plantuml2.get_url('txt', uml_helloworld_code) \
               == _append_path('txt/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80',
                               'https://demo-host-for-plantuml')
        assert plantuml2.get_url('svg', uml_helloworld_code) \
               == _append_path('svg/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80',
                               'https://demo-host-for-plantuml')
        assert plantuml2.get_url('eps', uml_helloworld_code) \
               == _append_path('eps/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80',
                               'https://demo-host-for-plantuml')

    _TXT_SIZES = [224, 372]
    _PNG_SIZES = [3020, 2300]
    _SVG_SIZES = [2742, 2003]
    _EPS_SIZES = [11048, 7938]
    _PDF_SIZES = [1811] if not _has_cairosvg() else [6326]

    @classmethod
    def _size_check(cls, expected_sizes: List[int], size: int):
        ranges = [(int(0.8 * exp_size), int(1.2 * exp_size)) for exp_size in expected_sizes]
        assert any(l <= size <= r for l, r in ranges), \
            f'Size in range {ranges!r} expected, but {size!r} found.'

    def test_dump_txt(self, plantuml, uml_helloworld, uml_helloworld_code):
        txt_result = plantuml.dump_txt(uml_helloworld_code)

        assert 'Bob' in txt_result
        assert 'Alice' in txt_result
        assert 'hello' in txt_result

        self._size_check(self._TXT_SIZES, len(txt_result))

    def test_dump_binary_txt(self, plantuml, uml_helloworld, uml_helloworld_code):
        _data = plantuml.dump_binary('txt', uml_helloworld_code)
        assert isinstance(_data, bytes)
        self._size_check(self._TXT_SIZES, len(_data))

    def test_dump_binary_png(self, plantuml, uml_helloworld, uml_helloworld_code):
        _data = plantuml.dump_binary('png', uml_helloworld_code)
        assert isinstance(_data, bytes)
        self._size_check(self._PNG_SIZES, len(_data))

    def test_dump_binary_svg(self, plantuml, uml_helloworld, uml_helloworld_code):
        _data = plantuml.dump_binary('svg', uml_helloworld_code)
        assert isinstance(_data, bytes)
        self._size_check(self._SVG_SIZES, len(_data))

    def test_dump_binary_eps(self, plantuml, uml_helloworld, uml_helloworld_code):
        _data = plantuml.dump_binary('eps', uml_helloworld_code)
        assert isinstance(_data, bytes)
        self._size_check(self._EPS_SIZES, len(_data))

    def test_dump_binary_pdf(self, plantuml, uml_helloworld, uml_helloworld_code, is_official, plantuml_server_version):
        if not _has_cairosvg() and (is_official or plantuml_server_version < (1, 2023)):
            with pytest.raises(ValueError):
                plantuml.dump_binary('pdf', uml_helloworld_code)
        else:
            _data = plantuml.dump_binary('pdf', uml_helloworld_code)
            assert isinstance(_data, bytes)
            self._size_check(self._PDF_SIZES, len(_data))

    def test_dump_file_txt(self, plantuml, uml_helloworld, uml_helloworld_code):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'txt', uml_helloworld_code)
            assert os.path.exists(file.name)
            self._size_check(self._TXT_SIZES, os.path.getsize(file.name))

    def test_dump_file_png(self, plantuml, uml_helloworld, uml_helloworld_code):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'png', uml_helloworld_code)
            assert os.path.exists(file.name)
            self._size_check(self._PNG_SIZES, os.path.getsize(file.name))

    def test_dump_file_svg(self, plantuml, uml_helloworld, uml_helloworld_code):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'svg', uml_helloworld_code)
            assert os.path.exists(file.name)
            self._size_check(self._SVG_SIZES, os.path.getsize(file.name))

    def test_dump_file_eps(self, plantuml, uml_helloworld, uml_helloworld_code):
        with NamedTemporaryFile() as file:
            plantuml.dump(file.name, 'eps', uml_helloworld_code)
            assert os.path.exists(file.name)
            self._size_check(self._EPS_SIZES, os.path.getsize(file.name))

    def test_dump_file_pdf(self, plantuml, uml_helloworld, uml_helloworld_code, is_official, plantuml_server_version):
        if not _has_cairosvg() and (is_official or plantuml_server_version < (1, 2023)):
            with pytest.raises(ValueError), NamedTemporaryFile() as file:
                plantuml.dump(file.name, 'pdf', uml_helloworld_code)
        else:
            with NamedTemporaryFile() as file:
                plantuml.dump(file.name, 'pdf', uml_helloworld_code)
                assert os.path.exists(file.name)
                self._size_check(self._PDF_SIZES, os.path.getsize(file.name))


@pytest.mark.unittest
class TestModelsRemoteCommon:
    def test_find_plantuml_host_from_env(self):
        with patch.dict(os.environ, {'PLANTUML_HOST': OFFICIAL_PLANTUML_HOST}):
            assert find_plantuml_host_from_env() == OFFICIAL_PLANTUML_HOST
        with patch.dict(os.environ, {'PLANTUML_HOST': 'https://plantuml-host'}):
            assert find_plantuml_host_from_env() == 'https://plantuml-host'
        with patch.dict(os.environ, {'PLANTUML_HOST': ''}):
            assert not find_plantuml_host_from_env()

    def test_find_plantuml_host(self):
        assert find_plantuml_host('https://this-is-a-host') == 'https://this-is-a-host'
        assert find_plantuml_host(OFFICIAL_PLANTUML_HOST) == OFFICIAL_PLANTUML_HOST

        with patch.dict(os.environ, {'PLANTUML_HOST': OFFICIAL_PLANTUML_HOST}):
            assert find_plantuml_host('https://this-is-a-host') == 'https://this-is-a-host'
            assert find_plantuml_host(OFFICIAL_PLANTUML_HOST) == OFFICIAL_PLANTUML_HOST
            assert find_plantuml_host() == OFFICIAL_PLANTUML_HOST

        with patch.dict(os.environ, {'PLANTUML_HOST': 'https://plantuml-host'}):
            assert find_plantuml_host('https://this-is-a-host') == 'https://this-is-a-host'
            assert find_plantuml_host(OFFICIAL_PLANTUML_HOST) == OFFICIAL_PLANTUML_HOST
            assert find_plantuml_host() == 'https://plantuml-host'

        with patch.dict(os.environ, {'PLANTUML_HOST': ''}):
            assert find_plantuml_host('https://this-is-a-host') == 'https://this-is-a-host'
            assert find_plantuml_host(OFFICIAL_PLANTUML_HOST) == OFFICIAL_PLANTUML_HOST
            assert find_plantuml_host() == OFFICIAL_PLANTUML_HOST
