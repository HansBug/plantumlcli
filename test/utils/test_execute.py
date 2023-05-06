import os

import pytest
import where

from plantumlcli.utils import execute, CommandLineExecuteError


@pytest.mark.unittest
class TestUtilsExecute:
    def test_execute(self):
        _stdout, _stderr = execute('echo', 'this_is_content')

        assert 'this_is_content' in _stdout
        assert not _stderr

    def test_execute_error(self):
        with pytest.raises(CommandLineExecuteError) as r:
            execute(where.first('python'), '-c',
                    r'import sys;print(2345678);print(2333333, file=sys.stderr);raise RuntimeError;')

        err = r.value
        assert isinstance(err, CommandLineExecuteError)
        assert err.exitcode != 0
        assert '2345678' in err.stdout
        assert '2333333' in err.stderr
        assert err.command_line[1:] == \
               ('-c', r'import sys;print(2345678);print(2333333, file=sys.stderr);raise RuntimeError;')
        assert repr(err) == "<CommandLineExecuteError exitcode: 1, command_line: ({python}, '-c', " \
                            "'import sys;print(2345678);print(2333333, file=sys.stderr);raise RuntimeError;')>" \
            .format(python=repr(where.first('python')))


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
