import os
import re
import shutil
from tempfile import TemporaryDirectory, NamedTemporaryFile
from typing import Tuple, Optional, Mapping, Any

from .base import Plantuml, PlantumlResourceType, _has_cairosvg
from ..utils import load_binary_file, save_text_file, CommandLineExecuteError, execute

PLANTUML_JAR_ENV = 'PLANTUML_JAR'


def find_java_from_env() -> Optional[str]:
    return shutil.which('java')


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
        raise FileNotFoundError(f'Java executable {java!r} not found.')
    if not os.path.isfile(java):
        raise IsADirectoryError(f'Java executable {java!r} is not a file.')
    if not os.access(java, os.X_OK):
        raise PermissionError(f'Java executable {java!r} not executable.')  # pragma: no cover

    if not plantuml:
        raise ValueError('Plantuml jar file not given.')
    if not os.path.exists(plantuml):
        raise FileNotFoundError(f'Plantuml jar file {plantuml!r} not found.')
    if not os.path.isfile(plantuml):
        raise IsADirectoryError(f'Plantuml jar file {plantuml!r} is not a file.')
    if not os.access(plantuml, os.R_OK):
        raise PermissionError(f'Plantuml jar file {plantuml!r} not readable.')  # pragma: no cover


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
    def autoload(cls, java: Optional[str] = None, plantuml: Optional[str] = None, **kwargs) -> 'LocalPlantuml':
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

    def _check_version(self, version: str):
        if (not version) or ("plantuml" not in version.lower()):
            raise ValueError(f"Invalid version of plantuml - {version!r}.")

    def _get_version(self) -> str:
        _stdout, _ = self.__execute('-version')
        _lines = _stdout.strip().splitlines()
        _first_line = _lines[0].strip() if _lines else ''
        _line, _ = re.subn(r'\([^()]*?\)', '', _first_line)
        _line, _ = re.subn(r'\\s+', '', _line)
        return _line.strip()

    def _generate_uml_data(self, type_: PlantumlResourceType, code: str) -> bytes:
        if type_ == PlantumlResourceType.PDF and _has_cairosvg():
            import cairosvg

            return cairosvg.svg2pdf(bytestring=self._generate_uml_data(PlantumlResourceType.SVG, code))
        else:
            with TemporaryDirectory(prefix='puml') as output_path_name:
                with NamedTemporaryFile(prefix='puml', suffix='.puml') as input_file:
                    save_text_file(input_file.name, code)
                    self.__execute(f'-t{type_.name.lower()}', '-o', output_path_name, input_file.name)
                    _file_list = os.listdir(output_path_name)
                    if _file_list:
                        output_filename = os.path.join(output_path_name, _file_list[0])
                        return load_binary_file(output_filename)
                    else:
                        # When you see this error, it means bug, please open an issue for help us fix this
                        raise FileNotFoundError(f'No expected file found in {output_path_name!r}.')  # pragma: no cover
