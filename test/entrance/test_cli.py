import os

import pytest
from click.testing import CliRunner

from plantumlcli.entrance import cli
from ..test import unittest, PRIMARY_JAR_PATH, is_file_func, mark_select

_primary_jar_condition = is_file_func(PRIMARY_JAR_PATH)


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

    if __name__ == "__main__":
        pytest.main([os.path.abspath(__file__)])
