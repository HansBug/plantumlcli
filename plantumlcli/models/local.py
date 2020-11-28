import os
import re
from tempfile import TemporaryDirectory, NamedTemporaryFile
from typing import Tuple, Optional, Mapping, Any

import where

from .base import Plantuml, PlantumlResourceType
from ..utils import load_binary_file, save_text_file, CommandLineExecuteError, execute

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


class LocalPlantumlExecuteError(CommandLineExecuteError):
    pass


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
        return execute(self.__java, '-jar', self.__plantuml, *args, exc=LocalPlantumlExecuteError)

    @classmethod
    def _check_version(cls, version: str):
        if (not version) or ("plantuml" not in version.lower()):
            raise ValueError("Invalid version of plantuml - {version}.".format(version=repr(version)))

    def _get_version(self) -> str:
        _stdout, _ = self.__execute('-version')
        _lines = _stdout.strip().splitlines()
        _first_line = _lines[0].strip() if _lines else ''
        _line, _ = re.subn(r'\([^()]*?\)', '', _first_line)
        _line, _ = re.subn(r'\\s+', '', _line)
        return _line.strip()

    def _generate_uml_data(self, type_: PlantumlResourceType, code: str) -> bytes:
        with TemporaryDirectory(prefix='puml') as output_path_name:
            with NamedTemporaryFile(prefix='puml', suffix='.puml') as input_file:
                save_text_file(input_file.name, code)
                self.__execute('-t{type}'.format(type=type_.name.lower()), '-o', output_path_name, input_file.name)
                _file_list = os.listdir(output_path_name)
                if _file_list:
                    output_filename = os.path.join(output_path_name, _file_list[0])
                    return load_binary_file(output_filename)
                else:
                    raise FileNotFoundError('No expected file found in {path}.'.format(path=repr(output_path_name)))
