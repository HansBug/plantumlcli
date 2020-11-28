import os

import pytest
from click.testing import CliRunner

from plantumlcli.entrance import cli
from plantumlcli.utils import all_func
from ..test import unittest, PRIMARY_JAR_PATH, is_file_func, mark_select, DEMO_HELLOWORLD_PUML, DEMO_COMMON_PUML, \
    DEMO_CHINESE_PUML, DEMO_LARGE_PUML

_primary_jar_condition = is_file_func(PRIMARY_JAR_PATH)
_helloworld_condition = is_file_func(DEMO_HELLOWORLD_PUML)
_common_condition = is_file_func(DEMO_COMMON_PUML)
_chinese_condition = is_file_func(DEMO_CHINESE_PUML)
_large_condition = is_file_func(DEMO_LARGE_PUML)
_all_puml_condition = all_func(_helloworld_condition, _chinese_condition, _chinese_condition, _large_condition)


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
        assert _lines[1] == 'http://www.plantuml.com/plantuml/uml/LP2n3eCm34HtVuN5M8aVw50XjKlNhbM7a1Ym6X84GOY_' \
                            'hmC4g9JXSk-Sir8CGVLXR2qqR0YfxSACXWRTSnVOEm091CBiQInbg0Pa4SbyiQlbB7w_weGUYcr2XfKze' \
                            'RkoEzAh1dXVFfZVbjVnYfsVg4UfN-xYHxpRLGKxs6e5ijE-ZJA-2ScNoDOHvrb_SUoEwMqpGNuCjT-da_' \
                            'ytNH8gDyW6PCw1RMNdIszcW9JFZP_SWHibdbGNv4pyxXy%3D'
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
        assert _lines[1] == 'http://this-is-a-host/uml/LP2n3eCm34HtVuN5M8aVw50XjKlNhbM7a1Ym6X84GOY_' \
                            'hmC4g9JXSk-Sir8CGVLXR2qqR0YfxSACXWRTSnVOEm091CBiQInbg0Pa4SbyiQlbB7w_weGUYcr2XfKze' \
                            'RkoEzAh1dXVFfZVbjVnYfsVg4UfN-xYHxpRLGKxs6e5ijE-ZJA-2ScNoDOHvrb_SUoEwMqpGNuCjT-da_' \
                            'ytNH8gDyW6PCw1RMNdIszcW9JFZP_SWHibdbGNv4pyxXy%3D'
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

    if __name__ == "__main__":
        pytest.main([os.path.abspath(__file__)])
