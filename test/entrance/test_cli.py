import os

import pytest
from click.testing import CliRunner

from plantumlcli.entrance import cli
from ..test import unittest, PRIMARY_JAR_PATH, is_file_func, mark_select, DEMO_HELLOWORLD_PUML

_primary_jar_condition = is_file_func(PRIMARY_JAR_PATH)
_helloworld_condition = is_file_func(DEMO_HELLOWORLD_PUML)


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

    @mark_select(_helloworld_condition)
    def test_homepage_url(self):
        runner = CliRunner()
        result = runner.invoke(cli, args=['--homepage-url', DEMO_HELLOWORLD_PUML])

        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 1
        assert _lines[0] == 'http://www.plantuml.com/plantuml/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['--homepage-url', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML])

        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://www.plantuml.com/plantuml/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://www.plantuml.com/plantuml/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

        result = runner.invoke(cli, args=['--homepage-url', DEMO_HELLOWORLD_PUML, DEMO_HELLOWORLD_PUML],
                               env={'PLANTUML_HOST': 'http://this-is-a-host'})
        assert result.exit_code == 0
        _lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        assert len(_lines) == 2
        assert _lines[0] == 'http://this-is-a-host/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'
        assert _lines[1] == 'http://this-is-a-host/uml/SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IG80'

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
