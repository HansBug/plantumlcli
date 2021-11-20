import os
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from plantumlcli.entrance import cli
from plantumlcli.models import Plantuml
from plantumlcli.utils import all_func
from requests import HTTPError

from ..test import unittest, PRIMARY_JAR_PATH, is_file_func, mark_select, DEMO_HELLOWORLD_PUML, DEMO_COMMON_PUML, \
    DEMO_CHINESE_PUML, DEMO_LARGE_PUML, DEMO_INVALID_PUML, TEST_PLANTUML_HOST, exist_func, DEMO_HELLOWORLD_PUML_ABS, \
    DEMO_CHINESE_PUML_ABS, DEMO_LARGE_PUML_ABS, DEMO_COMMON_PUML_ABS, DEMO_INVALID_PUML_ABS

_primary_jar_condition = is_file_func(PRIMARY_JAR_PATH)
_helloworld_condition = is_file_func(DEMO_HELLOWORLD_PUML)
_common_condition = is_file_func(DEMO_COMMON_PUML)
_chinese_condition = is_file_func(DEMO_CHINESE_PUML)
_large_condition = is_file_func(DEMO_LARGE_PUML)
_invalid_condition = is_file_func(DEMO_INVALID_PUML)

_all_puml_condition = all_func(_helloworld_condition, _chinese_condition, _chinese_condition, _large_condition)
_all_with_invalid_condition = all_func(_all_puml_condition, _invalid_condition)

_test_host_condition = exist_func(TEST_PLANTUML_HOST)


# noinspection DuplicatedCode
class TestEntranceCli:
    @unittest
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-v'])

        assert result.exit_code == 0
        assert "plantumlcli" in result.stdout.lower()

    @mark_select(_primary_jar_condition)
    def test_check_both(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-c'])

        assert result.exit_code == 0
        assert "Local plantuml not detected or has problem." in result.stdout
        assert "Remote plantuml detected." in result.stdout

        result = runner.invoke(cli, args=['-c'],
                               env={'PLANTUML_JAR': PRIMARY_JAR_PATH, 'PLANTUML_HOST': 'http://this-is-invalid-host'})

        assert result.exit_code == 0
        assert "Local plantuml detected." in result.stdout
        assert "Remote plantuml not detected or has problem." in result.stdout

        result = runner.invoke(cli, args=['-c'], env={'PLANTUML_JAR': PRIMARY_JAR_PATH})

        assert result.exit_code == 0
        assert "Local plantuml detected." in result.stdout
        assert "Remote plantuml detected." in result.stdout

    @unittest
    def test_check_both_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-c'], env={'PLANTUML_HOST': 'http://this-is-invalid-host'})

        assert result.exit_code != 0
        assert "Local plantuml not detected or has problem." in result.stdout
        assert "Remote plantuml not detected or has problem." in result.stdout

    @unittest
    def test_check_remote(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-cR'])

        assert result.exit_code == 0
        assert "Local plantuml detected." not in result.stdout
        assert "Local plantuml not detected or has problem." not in result.stdout
        assert "Remote plantuml detected." in result.stdout

    @unittest
    def test_check_remote_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-cR'], env={'PLANTUML_HOST': 'http://this-is-invalid-host'})

        assert result.exit_code != 0
        assert "Local plantuml detected." not in result.stdout
        assert "Local plantuml not detected or has problem." not in result.stdout
        assert "Remote plantuml not detected or has problem." in result.stdout

    @unittest
    def test_check_local(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-cL'], env={'PLANTUML_JAR': PRIMARY_JAR_PATH})

        assert result.exit_code == 0
        assert "Local plantuml detected." in result.stdout
        assert "Remote plantuml detected." not in result.stdout
        assert "Remote plantuml not detected or has problem." not in result.stdout

    @unittest
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

    @mark_select(_all_puml_condition)
    def test_homepage_url(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['--homepage-url', DEMO_HELLOWORLD_PUML])

        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 1
        assert _lines[0] == 'http://www.plantuml.com/plantuml/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['--homepage-url', DEMO_HELLOWORLD_PUML, DEMO_COMMON_PUML,
                                          DEMO_CHINESE_PUML, DEMO_LARGE_PUML])

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

        result = runner.invoke(cli, args=['--homepage-url', DEMO_HELLOWORLD_PUML, DEMO_COMMON_PUML,
                                          DEMO_CHINESE_PUML, DEMO_LARGE_PUML],
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

    @mark_select(_helloworld_condition)
    def test_homepage_url_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['--homepage-url', DEMO_HELLOWORLD_PUML, '-r', 'socks5://this-is-a-host'])

        assert result.exit_code != 0

    @mark_select(_helloworld_condition)
    def test_url(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-u', DEMO_HELLOWORLD_PUML])

        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 1
        assert _lines[0] == 'http://www.plantuml.com/plantuml/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML])

        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://www.plantuml.com/plantuml/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://www.plantuml.com/plantuml/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', '-t', 'txt', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/txt/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/txt/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', '-t', 'png', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/png/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', '-t', 'eps', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/eps/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/eps/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['-u', '-t', 'svg', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/svg/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/svg/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

    @mark_select(_helloworld_condition)
    def test_url_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-u', DEMO_HELLOWORLD_PUML, '-r', 'socks5://this-is-a-host'])

        assert result.exit_code != 0

    @mark_select(_helloworld_condition)
    def test_concurrency_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-u', '-n', '4', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML,
                                          DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML])

        assert result.exit_code == 0

    @mark_select(_helloworld_condition)
    def test_concurrency_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-u', '-n', '0', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML])

        assert result.exit_code != 0

    @mark_select(_all_puml_condition)
    def test_text_graph(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-T', DEMO_HELLOWORLD_PUML, DEMO_COMMON_PUML,
                                          DEMO_CHINESE_PUML, DEMO_LARGE_PUML])

        assert result.exit_code == 0
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

    @mark_select(all_func(_all_with_invalid_condition, _test_host_condition, _primary_jar_condition))
    def test_text_graph_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-T', DEMO_HELLOWORLD_PUML, DEMO_COMMON_PUML, DEMO_INVALID_PUML,
                                          DEMO_CHINESE_PUML, DEMO_LARGE_PUML],
                               env={'PLANTUML_HOST': TEST_PLANTUML_HOST})

        assert result.exit_code == -2
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert 'Syntax Error' in result.stdout
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

        result = runner.invoke(cli, args=['-T', DEMO_HELLOWORLD_PUML, DEMO_COMMON_PUML, DEMO_INVALID_PUML,
                                          DEMO_CHINESE_PUML, DEMO_LARGE_PUML],
                               env={'PLANTUML_JAR': PRIMARY_JAR_PATH})

        assert result.exit_code == -2
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert ('No diagram found' in result.stdout) or ('No expected file found' in result.stdout)
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

        runner = CliRunner()
        result = runner.invoke(cli, args=['-TR', DEMO_HELLOWORLD_PUML, DEMO_COMMON_PUML, DEMO_INVALID_PUML,
                                          DEMO_CHINESE_PUML, DEMO_LARGE_PUML],
                               env={'PLANTUML_HOST': TEST_PLANTUML_HOST})

        assert result.exit_code == -2
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert 'Syntax Error' in result.stdout
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

        result = runner.invoke(cli, args=['-TL', DEMO_HELLOWORLD_PUML, DEMO_COMMON_PUML, DEMO_INVALID_PUML,
                                          DEMO_CHINESE_PUML, DEMO_LARGE_PUML],
                               env={'PLANTUML_JAR': PRIMARY_JAR_PATH})

        assert result.exit_code == -2
        assert 'Alice' in result.stdout
        assert 'Dialing' in result.stdout
        assert ('No diagram found' in result.stdout) or ('No expected file found' in result.stdout)
        assert '认证中心' in result.stdout
        assert 'Handle claim' in result.stdout

        _dump_txt_func, Plantuml.dump_txt = Plantuml.dump_txt, Mock(
            side_effect=OSError('This is an os error.'))
        result = runner.invoke(cli, args=['-T', DEMO_HELLOWORLD_PUML], env={'PLANTUML_HOST': TEST_PLANTUML_HOST})
        assert result.exit_code != 0
        assert 'OSError' in result.stdout
        assert 'This is an os error.' in result.stdout
        Plantuml.dump_txt = _dump_txt_func

        _dump_txt_func, Plantuml.dump_txt = Plantuml.dump_txt, Mock(
            side_effect=HTTPError('This is a http error.'))
        result = runner.invoke(cli, args=['-T', DEMO_HELLOWORLD_PUML], env={'PLANTUML_HOST': TEST_PLANTUML_HOST})
        assert result.exit_code != 0
        assert 'HTTPError' in result.stdout
        assert 'This is a http error.' in result.stdout
        Plantuml.dump_txt = _dump_txt_func

    _EXPECTED_TXT_LENGTH_FOR_HELLOWORLD = 372
    _EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_1 = 3020
    _EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_2 = 2300
    _EXPECTED_SVG_LENGTH_FOR_HELLOWORLD = 2742
    _EXPECTED_EPS_LENGTH_FOR_HELLOWORLD = 11048

    _EXPECTED_EPS_LENGTH_FOR_COMMON = 28748
    _EXPECTED_EPS_LENGTH_FOR_CHINESE = 93907
    _EXPECTED_EPS_LENGTH_FOR_LARGE = 100685

    @mark_select(all_func(_all_puml_condition, _primary_jar_condition))
    def test_file_dump(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(cli, [DEMO_HELLOWORLD_PUML_ABS])

            assert result.exit_code == 0
            assert os.path.exists('helloworld.png')
            assert (self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_1 * 0.8 < os.path.getsize('helloworld.png')
                    < self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_1 * 1.2) or \
                   (self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_2 * 0.8 < os.path.getsize('helloworld.png')
                    < self._EXPECTED_PNG_LENGTH_FOR_HELLOWORLD_2 * 1.2)

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['-t', 'eps', DEMO_HELLOWORLD_PUML_ABS])

            assert result.exit_code == 0
            assert os.path.exists('helloworld.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize('helloworld.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2)

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', DEMO_HELLOWORLD_PUML_ABS])

            assert result.exit_code == 0
            assert os.path.exists('new_file.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize('new_file.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2)

        with runner.isolated_filesystem():
            os.makedirs('new/path', exist_ok=True)
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-O', 'new/path', DEMO_HELLOWORLD_PUML_ABS])

            assert result.exit_code == 0
            assert os.path.exists('new/path/new_file.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize('new/path/new_file.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2)

        with runner.isolated_filesystem():
            os.makedirs('new/path', exist_ok=True)
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-o', 'new_file_2.eps',
                                         '-O', 'new/path', DEMO_HELLOWORLD_PUML_ABS, DEMO_CHINESE_PUML_ABS])

            assert result.exit_code == 0
            assert os.path.exists('new/path/new_file.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize('new/path/new_file.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2)
            assert os.path.exists('new/path/new_file_2.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_CHINESE * 0.8 < os.path.getsize('new/path/new_file_2.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_CHINESE * 1.2)

        with runner.isolated_filesystem():
            os.makedirs('new/path', exist_ok=True)
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-o', 'new_file_2.eps',
                                         '-o', 'new_file_3.eps', '-o', 'new_file_4.eps',
                                         '-O', 'new/path', DEMO_HELLOWORLD_PUML_ABS, DEMO_COMMON_PUML_ABS,
                                         DEMO_CHINESE_PUML_ABS, DEMO_LARGE_PUML_ABS])

            assert result.exit_code == 0
            assert os.path.exists('new/path/new_file.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize('new/path/new_file.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2)
            assert os.path.exists('new/path/new_file_2.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_COMMON * 0.8 < os.path.getsize('new/path/new_file_2.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_COMMON * 1.2)
            assert os.path.exists('new/path/new_file_3.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_CHINESE * 0.8 < os.path.getsize('new/path/new_file_3.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_CHINESE * 1.2)
            assert os.path.exists('new/path/new_file_4.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_LARGE * 0.8 < os.path.getsize('new/path/new_file_4.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_LARGE * 1.2)

    @mark_select(all_func(_all_with_invalid_condition, _primary_jar_condition))
    def test_file_dump_error(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-o', 'new_file_2.eps',
                                         DEMO_HELLOWORLD_PUML_ABS])

            assert result.exit_code != 0

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['-t', 'eps', '-o', 'new_file.eps', '-o', 'new_file_2.eps', '-o',
                                         'new_file_3.eps', DEMO_HELLOWORLD_PUML_ABS, DEMO_INVALID_PUML_ABS,
                                         DEMO_COMMON_PUML_ABS])

            assert result.exit_code != 0
            assert os.path.exists('new_file.eps')
            assert (self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 0.8 < os.path.getsize('new_file.eps')
                    < self._EXPECTED_EPS_LENGTH_FOR_HELLOWORLD * 1.2)
            assert not os.path.exists('new_file_2.eps')
            assert not os.path.exists('new_file_3.eps')

    @mark_select(_helloworld_condition)
    def test_auto_select_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['-T', DEMO_HELLOWORLD_PUML],
                               env={'PLANTUML_HOST': 'socks5://this-is-an-invalid-host'})

        assert result.exit_code != 0


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
