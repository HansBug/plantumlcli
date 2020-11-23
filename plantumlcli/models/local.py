import re
import subprocess
from typing import Tuple, Optional

import where

from .base import Plantuml


def _decode_if_not_none(value: Optional[bytes]) -> Optional[str]:
    if value is not None:
        return value.decode()
    else:
        return value


class LocalPlantuml(Plantuml):
    def __init__(self, plantuml: str, java: str = None):
        Plantuml.__init__(self)
        self.__java = java or where.first('java')
        self.__plantuml = plantuml
        self.__version = None

    def __execute(self, *args) -> Tuple[str, str]:
        _cmdline = [self.__java, '-jar', self.__plantuml] + list(args)
        process = subprocess.Popen(
            args=_cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _stdout, _stderr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError('Error when executing {cmd}, return {ret}.'.format(
                cmd=repr(tuple(_cmdline)), ret=process.returncode
            ))
        return _decode_if_not_none(_stdout), _decode_if_not_none(_stderr)

    def _get_version(self) -> str:
        if not self.__version:
            _stdout, _ = self.__execute('-version')
            _first_line = _stdout.strip().splitlines()[0].strip()
            _line, _ = re.subn(r'\([^()]*?\)', '', _first_line)
            _line, _ = re.subn(r'\\s+', '', _line)
            self.__version = _line.strip()

        return self.__version

    def _check(self):
        if "plantuml" not in self._get_version().lower():
            raise ValueError("Invalid version of plantuml - {version}.".format(version=repr(self._get_version())))
