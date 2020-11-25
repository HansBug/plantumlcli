import os
import re
import subprocess
from typing import Tuple, Optional, Mapping, Any

import where

from .base import Plantuml, PlantumlResourceType

PLANTUML_JAR_ENV = 'PLANTUML_JAR'


def find_java_from_env() -> Optional[str]:
    return where.first('java')


def find_java(java: Optional[str] = None) -> Optional[str]:
    return java or find_java_from_env()


def find_plantuml_from_env() -> Optional[str]:
    return os.environ.get(PLANTUML_JAR_ENV, None)


def find_plantuml(plantuml: Optional[str] = None) -> Optional[str]:
    return plantuml or find_plantuml_from_env()


def _check_local(java: str, plantuml: str):
    if not java:
        raise ValueError('Java executable not given.')
    if not os.path.exists(java):
        raise FileNotFoundError('Java executable {exec} not found.'.format(exec=repr(java)))
    if not os.path.isfile(java):
        raise IsADirectoryError('Java executable {exec} is not a file.'.format(exec=repr(java)))
    if not os.access(java, os.X_OK):
        raise PermissionError('Java executable {exec} not executable.'.format(exec=repr(java)))

    if not plantuml:
        raise ValueError('Plantuml jar file not given.')
    if not os.path.exists(plantuml):
        raise FileNotFoundError('Plantuml jar file {jar} not found.'.format(jar=repr(plantuml)))
    if not os.path.isfile(plantuml):
        raise IsADirectoryError('Plantuml jar file {jar} is not a file.'.format(jar=repr(plantuml)))
    if not os.access(plantuml, os.R_OK):
        raise PermissionError('Plantuml jar file {jar} not readable.'.format(jar=repr(plantuml)))


def _decode_if_not_none(value: Optional[bytes]) -> Optional[str]:
    if value is not None:
        return value.decode()
    else:
        return value


class LocalPlantuml(Plantuml):
    def __init__(self, java: str, plantuml: str):
        """
        :param java: java executable file path
        :param plantuml: plantuml jar file path
        """
        Plantuml.__init__(self)

        self.__java = java
        self.__plantuml = plantuml
        _check_local(self.__java, self.__plantuml)

    @classmethod
    def autoload(cls, java: str = None, plantuml: str = None, **kwargs) -> 'LocalPlantuml':
        """
        Autoload LocalPlantuml object from given parameters and the environment
        :param java: java executable file path
        :param plantuml: plantuml jar file path
        :param kwargs: other arguments
        :return: local plantuml object
        """
        return LocalPlantuml(find_java(java), find_plantuml(plantuml))

    @property
    def java(self) -> str:
        """
        Java executable file path
        :return: java executable file path
        """
        return self.__java

    @property
    def plantuml(self) -> str:
        """
        Plantuml jar file path
        :return: plantuml jar file path
        """
        return self.__plantuml

    def _properties(self) -> Mapping[str, Any]:
        return {
            'java': self.__java,
            'plantuml': self.__plantuml,
        }

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

    @classmethod
    def _check_version(cls, version: str):
        if "plantuml" not in version.lower():
            raise ValueError("Invalid version of plantuml - {version}.".format(version=repr(version)))

    def _get_version(self) -> str:
        _stdout, _ = self.__execute('-version')
        _first_line = _stdout.strip().splitlines()[0].strip()
        _line, _ = re.subn(r'\([^()]*?\)', '', _first_line)
        _line, _ = re.subn(r'\\s+', '', _line)
        return _line.strip()

    def _generate_uml_data(self, type_: PlantumlResourceType, code: str) -> bytes:
        pass
        # self.__execute('-t{type}'.format(type=type_.name.lower()))
