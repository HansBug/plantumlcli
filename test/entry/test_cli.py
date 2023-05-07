import os
from typing import List
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from requests import HTTPError

from plantumlcli.entry import cli
from plantumlcli.models import Plantuml
from .conftest import _has_cairosvg


# noinspection DuplicatedCode,PyTypeChecker,HttpUrlsUsage
@pytest.mark.unittest
class TestEntranceCli:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-v'])

        assert result.exit_code == 0
        assert "plantumlcli" in result.stdout.lower()

    def test_check_both(self, plantuml_jar_file):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-c'])

        assert result.exit_code == 0
        assert "Local plantuml not detected or has problem." in result.stdout
        assert "Remote plantuml detected." in result.stdout

        result = runner.invoke(cli, args=['-c'],
                               env={'PLANTUML_JAR': plantuml_jar_file, 'PLANTUML_HOST': 'http://this-is-invalid-host'})

        assert result.exit_code == 0
        assert "Local plantuml detected." in result.stdout
        assert "Remote plantuml not detected or has problem." in result.stdout

        result = runner.invoke(cli, args=['-c'], env={'PLANTUML_JAR': plantuml_jar_file})

        assert result.exit_code == 0
        assert "Local plantuml detected." in result.stdout
        assert "Remote plantuml detected." in result.stdout

    def test_check_both_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-c'], env={'PLANTUML_HOST': 'http://this-is-invalid-host'})

        assert result.exit_code != 0
        assert "Local plantuml not detected or has problem." in result.stdout
        assert "Remote plantuml not detected or has problem." in result.stdout

    def test_check_remote(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-cR'])

        assert result.exit_code == 0
        assert "Local plantuml detected." not in result.stdout
        assert "Local plantuml not detected or has problem." not in result.stdout
        assert "Remote plantuml detected." in result.stdout

    def test_check_remote_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-cR'], env={'PLANTUML_HOST': 'http://this-is-invalid-host'})

        assert result.exit_code != 0
        assert "Local plantuml detected." not in result.stdout
        assert "Local plantuml not detected or has problem." not in result.stdout
        assert "Remote plantuml not detected or has problem." in result.stdout

    def test_check_local(self, plantuml_jar_file):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-cL'], env={'PLANTUML_JAR': plantuml_jar_file})

        assert result.exit_code == 0
        assert "Local plantuml detected." in result.stdout
        assert "Remote plantuml detected." not in result.stdout
        assert "Remote plantuml not detected or has problem." not in result.stdout

    def test_check_local_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-cL'])

        assert result.exit_code != 0
        assert "Local plantuml not detected or has problem." in result.stdout
        assert "Remote plantuml detected." not in result.stdout
        assert "Remote plantuml not detected or has problem." not in result.stdout

        result = runner.invoke(cli, args=['-cL'], env={'PLANTUML_JAR': '/path/not/exist'})

        assert result.exit_code != 0
        assert "Local plantuml not detected or has problem." in result.stdout
        assert "Remote plantuml detected." not in result.stdout
        assert "Remote plantuml not detected or has problem." not in result.stdout

    def test_homepage_url(self, uml_helloworld, uml_common, uml_chinese, uml_large):
        runner = CliRunner()
        result = runner.invoke(cli, args=['--homepage-url', uml_helloworld], env={'PLANTUML_HOST': ''})

        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 1
        assert _lines[0] == 'http://www.plantuml.com/plantuml/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['--homepage-url', uml_helloworld, uml_common,
                                          uml_chinese, uml_large], env={'PLANTUML_HOST': ''})

        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 4
        assert _lines[0] == 'http://www.plantuml.com/plantuml/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://www.plantuml.com/plantuml/uml/LP2n3eCm34HtVuN5M8aVw50XjKlNhbM7a1Y86k88WX1_' \
                            'NmS8RQKCbtldd9LgZ6g8K--WiuQG-X0ND3JgmOPesGD8818MT-EeG3MY5P7DX_MjdDKVDftHpIgNaTbqH' \
                            'bVb3gGt3V0ylR2yhA_Z6GFFDA3KhtVn4pxife43xBK2hTVS9vdUXEnBPEz8yrQ_SGhVwNqpGJp5be_fxF' \
                            'zDruJAZx81cT_0lhBdciq2aFEbuTb_SQV4a-gAl4dV_G4%3D'
        assert _lines[2] == 'http://www.plantuml.com/plantuml/uml/SoWkIImgAStDuNe-PSMpZkqAkdOABzOjUR6-yScEjK_t' \
                            'DrifF9-v--dUgSyczpxPEuSBMGgazFcUoK_Nph1I01BFfkpJo4wjj2t9pqxDqyuiq2bBp2bDXN0rmIGNp' \
                            '0uRNHGx5AoWt6ST4vvspN-nVyhJsVCWEd0vwicExcTh5hvOj__bz7LFbsnvsRpYsOHTJtSi0-k2A4LrAz' \
                            '1Ac5kH7VcYR_lJ_caGkvwsRdkoUzgpERrFknQYEn7imwTpLZpPCUNPWeKlL_L0dFgqO-QBxPjVx5tpj6C' \
                            '3nAalrcz_jh7f-QmMPDDGZGO56rWjq1lx5pvhNC_ba9gN0ee200%3D%3D'
        assert _lines[3] == 'http://www.plantuml.com/plantuml/uml/fLLDRzim33rFlqBeXc4Ru0uOi4kH1VNIjScXdR40EVN2' \
                            'saoYrQ8CIMvNRFtle-puAqk3fiiX2KNoYO-ao5FdmVfIvyBTAYh0WfOMKm-qod4qki4rt2bZnsFvMxoof' \
                            'gHiOYoXbPy-YqVX2giyoZStYJKfEYT_WZq1cwwL1eyVRqgdY8-ZebQtzZ17UwTItBA7eiXL2buPYbnjqR' \
                            'bCZ2uC8VazJcbZ8qHBGXvDWJB-JNDG-aXAS78waQDH6_LuF23w-kicx3x610fVMfGpMXghgzjggCdiKAW' \
                            'huzNouPhYB5C11t8vzt2BQvDdQDrHGBsAvuV2BY1N6IUaybySwZsZEtHUhHg0Wraby50v9izo55o13r5c' \
                            'xYdY3FObPjuN5trXO9W8mRcFh5gjVSJWmJ6ahJjPY4LFcec-TJBea7aAH8fM5GEt4GAHfb6tYSHTqmswf' \
                            '7JUQ7uTa6bIpjjDep1gkb75cLQTwYLtX3Pskswe5F-BdrX5_aNikGDqU9xFT1HjdgEoYCQX3Px8KSzW5y' \
                            'LQ6yg_HxtOfvo99lPQvkPeqz2uRnqC--VCf6NmlwPB85XX_N_-u3pggZPdbzLxxeROdW9V8CzNoAzfykD' \
                            'o0CBoFo1FeamvaVAjZE-1HqrYsAGQENts5UWqJk9dXpO0FLS4bAeGwIxSynsuMnqGid9S5iT_nksZwvyr' \
                            'AHU1-EPiTuk8YaLZigFGeWgdmQsBBKIEAwHCvhZqujilq0LpN5gZfLypsJYi65TQ9idB0nnAvykCfzoxx' \
                            'mNI1I_3ulsnc2EAB_mHlQadJvhD9vlDjp5f7uOyaRt59PjjrvXrITiox3OSXgKMuXUd_1Ks-5y%3D'

        result = runner.invoke(cli, args=['--homepage-url', uml_helloworld, uml_common,
                                          uml_chinese, uml_large],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 4

        assert _lines[0] == 'http://this-is-a-host/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/uml/LP2n3eCm34HtVuN5M8aVw50XjKlNhbM7a1Y86k88WX1_' \
                            'NmS8RQKCbtldd9LgZ6g8K--WiuQG-X0ND3JgmOPesGD8818MT-EeG3MY5P7DX_MjdDKVDftHpIgNaTbqH' \
                            'bVb3gGt3V0ylR2yhA_Z6GFFDA3KhtVn4pxife43xBK2hTVS9vdUXEnBPEz8yrQ_SGhVwNqpGJp5be_fxF' \
                            'zDruJAZx81cT_0lhBdciq2aFEbuTb_SQV4a-gAl4dV_G4%3D'
        assert _lines[2] == 'http://this-is-a-host/uml/SoWkIImgAStDuNe-PSMpZkqAkdOABzOjUR6-yScEjK_t' \
                            'DrifF9-v--dUgSyczpxPEuSBMGgazFcUoK_Nph1I01BFfkpJo4wjj2t9pqxDqyuiq2bBp2bDXN0rmIGNp' \
                            '0uRNHGx5AoWt6ST4vvspN-nVyhJsVCWEd0vwicExcTh5hvOj__bz7LFbsnvsRpYsOHTJtSi0-k2A4LrAz' \
                            '1Ac5kH7VcYR_lJ_caGkvwsRdkoUzgpERrFknQYEn7imwTpLZpPCUNPWeKlL_L0dFgqO-QBxPjVx5tpj6C' \
                            '3nAalrcz_jh7f-QmMPDDGZGO56rWjq1lx5pvhNC_ba9gN0ee200%3D%3D'
        assert _lines[3] == 'http://this-is-a-host/uml/fLLDRzim33rFlqBeXc4Ru0uOi4kH1VNIjScXdR40EVN2' \
                            'saoYrQ8CIMvNRFtle-puAqk3fiiX2KNoYO-ao5FdmVfIvyBTAYh0WfOMKm-qod4qki4rt2bZnsFvMxoof' \
                            'gHiOYoXbPy-YqVX2giyoZStYJKfEYT_WZq1cwwL1eyVRqgdY8-ZebQtzZ17UwTItBA7eiXL2buPYbnjqR' \
                            'bCZ2uC8VazJcbZ8qHBGXvDWJB-JNDG-aXAS78waQDH6_LuF23w-kicx3x610fVMfGpMXghgzjggCdiKAW' \
                            'huzNouPhYB5C11t8vzt2BQvDdQDrHGBsAvuV2BY1N6IUaybySwZsZEtHUhHg0Wraby50v9izo55o13r5c' \
                            'xYdY3FObPjuN5trXO9W8mRcFh5gjVSJWmJ6ahJjPY4LFcec-TJBea7aAH8fM5GEt4GAHfb6tYSHTqmswf' \
                            '7JUQ7uTa6bIpjjDep1gkb75cLQTwYLtX3Pskswe5F-BdrX5_aNikGDqU9xFT1HjdgEoYCQX3Px8KSzW5y' \
                            'LQ6yg_HxtOfvo99lPQvkPeqz2uRnqC--VCf6NmlwPB85XX_N_-u3pggZPdbzLxxeROdW9V8CzNoAzfykD' \
                            'o0CBoFo1FeamvaVAjZE-1HqrYsAGQENts5UWqJk9dXpO0FLS4bAeGwIxSynsuMnqGid9S5iT_nksZwvyr' \
                            'AHU1-EPiTuk8YaLZigFGeWgdmQsBBKIEAwHCvhZqujilq0LpN5gZfLypsJYi65TQ9idB0nnAvykCfzoxx' \
                            'mNI1I_3ulsnc2EAB_mHlQadJvhD9vlDjp5f7uOyaRt59PjjrvXrITiox3OSXgKMuXUd_1Ks-5y%3D'

    def test_homepage_url_error(self, uml_helloworld):
        runner = CliRunner()
        result = runner.invoke(cli, args=['--homepage-url', uml_helloworld, '-r', 'socks5://this-is-a-host'])

        assert result.exit_code != 0

    def test_url(self, uml_helloworld):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-u', uml_helloworld], env={'PLANTUML_HOST': ''})

        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 1
        assert _lines[0] == 'http://www.plantuml.com/plantuml/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', uml_helloworld, uml_helloworld], env={'PLANTUML_HOST': ''})

        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://www.plantuml.com/plantuml/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://www.plantuml.com/plantuml/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', uml_helloworld, uml_helloworld],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', '-t', 'txt', uml_helloworld, uml_helloworld],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/txt/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/txt/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', '-t', 'png', uml_helloworld, uml_helloworld],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', '-t', 'eps', uml_helloworld, uml_helloworld],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/eps/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/eps/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', '-t', 'svg', uml_helloworld, uml_helloworld],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/svg/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/svg/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

    def test_url_error(self, uml_helloworld):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-u', uml_helloworld, '-r', 'socks5://this-is-a-host'])

        assert result.exit_code != 0

    def test_concurrency(self, uml_helloworld):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-u', '-n', '4', uml_helloworld, uml_helloworld,
                                          uml_helloworld, uml_helloworld])

        assert result.exit_code == 0

    def test_concurrency_error(self, uml_helloworld):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-u', '-n', '0', uml_helloworld, uml_helloworld])

        assert result.exit_code != 0

    def test_text_graph(self, uml_helloworld, uml_common, uml_chinese, uml_large):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-T', uml_helloworld, uml_common,
                                          uml_chinese, uml_large])

        assert result.exit_code == 0
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

    def test_text_graph_error(self, plantuml_jar_file, plantuml_host,
                              uml_helloworld, uml_common, uml_invalid, uml_chinese, uml_large):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-T', uml_helloworld, uml_common, uml_invalid,
                                          uml_chinese, uml_large],
                               env={'PLANTUML_HOST': plantuml_host})

        assert result.exit_code == -2
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert 'Syntax Error' in result.stdout
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

        result = runner.invoke(cli, args=['-T', uml_helloworld, uml_common, uml_invalid,
                                          uml_chinese, uml_large],
                               env={'PLANTUML_JAR': plantuml_jar_file})

        assert result.exit_code == -2
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert ('No diagram found' in result.stdout) or ('No expected file found' in result.stdout)
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

        runner = CliRunner()
        result = runner.invoke(cli, args=['-TR', uml_helloworld, uml_common, uml_invalid,
                                          uml_chinese, uml_large],
                               env={'PLANTUML_HOST': plantuml_host})

        assert result.exit_code == -2
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert 'Syntax Error' in result.stdout
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

        result = runner.invoke(cli, args=['-TL', uml_helloworld, uml_common, uml_invalid,
                                          uml_chinese, uml_large],
                               env={'PLANTUML_JAR': plantuml_jar_file})

        assert result.exit_code == -2
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert ('No diagram found' in result.stdout) or ('No expected file found' in result.stdout)
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

        _dump_txt_func, Plantuml.dump_txt = Plantuml.dump_txt, Mock(
            side_effect=OSError('This is an os error.'))
        result = runner.invoke(cli, args=['-T', uml_helloworld], env={'PLANTUML_HOST': plantuml_host})
        assert result.exit_code != 0
        assert 'OSError' in result.stdout
        assert 'This is an os error.' in result.stdout
        Plantuml.dump_txt = _dump_txt_func

        _dump_txt_func, Plantuml.dump_txt = Plantuml.dump_txt, Mock(
            side_effect=HTTPError('This is a http error.'))
        result = runner.invoke(cli, args=['-T', uml_helloworld], env={'PLANTUML_HOST': plantuml_host})
        assert result.exit_code != 0
        assert 'HTTPError' in result.stdout
        assert 'This is a http error.' in result.stdout
        Plantuml.dump_txt = _dump_txt_func

    _TXT_SIZES = [224, 372]
    _PNG_SIZES = [3020, 2300]
    _SVG_SIZES = [2742, 2003]
    _EPS_SIZES = [11048, 7938]
    _PDF_SIZES = [1811] if not _has_cairosvg() else [6326]
    _EPS_COMMON_SIZES = [28748]
    _EPS_CHINESE_SIZES = [93907, 74166]
    _EPS_LARGE_SIZES = [100685]

    @classmethod
    def _size_check(cls, expected_sizes: List[int], size: int):
        ranges = [(int(0.8 * exp_size), int(1.2 * exp_size)) for exp_size in expected_sizes]
        assert any(l <= size <= r for l, r in ranges), \
            f'Size in range {ranges!r} expected, but {size!r} found.'

    def test_file_dump(self, uml_helloworld, uml_common, uml_chinese, uml_large, plantuml_server_version):
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(cli, [os.path.abspath(uml_helloworld)])

            assert result.exit_code == 0
            assert os.path.exists('helloworld.png')
            self._size_check(self._PNG_SIZES, os.path.getsize('helloworld.png'))

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['-t', 'eps', os.path.abspath(uml_helloworld)])

            assert result.exit_code == 0
            assert os.path.exists('helloworld.eps')
            self._size_check(self._EPS_SIZES, os.path.getsize('helloworld.eps'))

        if plantuml_server_version >= (1, 2023) or _has_cairosvg():
            with runner.isolated_filesystem():
                result = runner.invoke(cli, ['-t', 'pdf', os.path.abspath(uml_helloworld)])

                assert result.exit_code == 0
                assert os.path.exists('helloworld.pdf')
                self._size_check(self._PDF_SIZES, os.path.getsize('helloworld.pdf'))

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', os.path.abspath(uml_helloworld)])

            assert result.exit_code == 0
            assert os.path.exists('new_file.eps')
            self._size_check(self._EPS_SIZES, os.path.getsize('new_file.eps'))

        with runner.isolated_filesystem():
            os.makedirs('new/path', exist_ok=True)
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-O', 'new/path',
                                         os.path.abspath(uml_helloworld)])

            assert result.exit_code == 0
            assert os.path.exists('new/path/new_file.eps')
            self._size_check(self._EPS_SIZES, os.path.getsize('new/path/new_file.eps'))

        with runner.isolated_filesystem():
            os.makedirs('new/path', exist_ok=True)
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-o', 'new_file_2.eps',
                                         '-O', 'new/path', os.path.abspath(uml_helloworld),
                                         os.path.abspath(uml_chinese)])

            assert result.exit_code == 0
            assert os.path.exists('new/path/new_file.eps')
            self._size_check(self._EPS_SIZES, os.path.getsize('new/path/new_file.eps'))
            assert os.path.exists('new/path/new_file_2.eps')
            self._size_check(self._EPS_CHINESE_SIZES, os.path.getsize('new/path/new_file_2.eps'))

        with runner.isolated_filesystem():
            os.makedirs('new/path', exist_ok=True)
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-o', 'new_file_2.eps',
                                         '-o', 'new_file_3.eps', '-o', 'new_file_4.eps',
                                         '-O', 'new/path', os.path.abspath(uml_helloworld), os.path.abspath(uml_common),
                                         os.path.abspath(uml_chinese), os.path.abspath(uml_large)])

            assert result.exit_code == 0
            assert os.path.exists('new/path/new_file.eps')
            self._size_check(self._EPS_SIZES, os.path.getsize('new/path/new_file.eps'))
            assert os.path.exists('new/path/new_file_2.eps')
            self._size_check(self._EPS_COMMON_SIZES, os.path.getsize('new/path/new_file_2.eps'))
            assert os.path.exists('new/path/new_file_3.eps')
            self._size_check(self._EPS_CHINESE_SIZES, os.path.getsize('new/path/new_file_3.eps'))
            assert os.path.exists('new/path/new_file_4.eps')
            self._size_check(self._EPS_LARGE_SIZES, os.path.getsize('new/path/new_file_4.eps'))

    def test_file_dump_error(self, uml_helloworld, uml_common, uml_invalid):
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-o', 'new_file_2.eps',
                                         os.path.abspath(uml_helloworld)])

            assert result.exit_code != 0

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-o', 'new_file_2.eps', '-o',
                                         'new_file_3.eps', os.path.abspath(uml_helloworld),
                                         os.path.abspath(uml_invalid),
                                         os.path.abspath(uml_common)])

            assert result.exit_code != 0
            assert os.path.exists('new_file.eps')
            self._size_check(self._EPS_SIZES, os.path.getsize('new_file.eps'))
            assert not os.path.exists('new_file_2.eps')
            assert not os.path.exists('new_file_3.eps')

    def test_auto_select_error(self, uml_helloworld):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-T', uml_helloworld],
                               env={'PLANTUML_HOST': 'socks5://this-is-an-invalid-host'})

        assert result.exit_code != 0
