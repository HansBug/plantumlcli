import subprocess
from typing import Tuple, Optional, Type


class CommandLineExecuteError(Exception):
    # noinspection PyUnusedLocal
    def __init__(self, command_line: Tuple[str], exitcode: int,
                 stdout: Optional[str] = None, stderr: Optional[str] = None, **kwargs):
        self.__command_line = command_line
        self.__exitcode = exitcode
        self.__stdout = stdout
        self.__stderr = stderr

    @property
    def command_line(self) -> Tuple[str]:
        return self.__command_line

    @property
    def exitcode(self) -> int:
        return self.__exitcode

    @property
    def stdout(self) -> Optional[str]:
        return self.__stdout

    @property
    def stderr(self) -> Optional[str]:
        return self.__stderr

    def __repr__(self):
        return '<{cls} exitcode: {code}, command_line: {cmd}>'.format(
            cls=self.__class__.__name__,
            cmd=repr(self.__command_line),
            code=repr(self.__exitcode),
        )

    @classmethod
    def try_raise(cls, command_line: Tuple[str], exitcode: int,
                  stdout: Optional[str] = None, stderr: Optional[str] = None, **kwargs):
        if exitcode != 0:
            raise cls(command_line, exitcode, stdout, stderr, **kwargs)


def _decode_if_not_none(value: Optional[bytes]) -> Optional[str]:
    if value is not None:
        return value.decode()
    else:
        return value


def execute(*cmdline: str, exc: Type[CommandLineExecuteError] = CommandLineExecuteError
            ) -> Tuple[Optional[str], Optional[str]]:
    process = subprocess.Popen(
        args=cmdline,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    _stdout, _stderr = process.communicate()
    _stdout, _stderr = _decode_if_not_none(_stdout), _decode_if_not_none(_stderr)

    exc.try_raise(cmdline, process.returncode, _stdout, _stderr)
    return _stdout, _stderr
