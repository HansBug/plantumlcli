from abc import ABCMeta, abstractmethod
from enum import IntEnum, unique
from typing import TypeVar, Type, Optional, Tuple, Union, Any, Mapping

from ..utils import check_func, save_binary_file, auto_decode


@unique
class PlantumlType(IntEnum):
    LOCAL = 1
    REMOTE = 2


@unique
class PlantumlResourceType(IntEnum):
    """
    More types will be added later
    """
    TXT = 1
    PNG = 2
    SVG = 3
    EPS = 4

    @classmethod
    def load(cls, data: Union[int, str, 'PlantumlResourceType']) -> 'PlantumlResourceType':
        if isinstance(data, PlantumlResourceType):
            return data
        elif isinstance(data, int):
            if data in cls.__members__.values():
                return cls.__members__[dict(zip(cls.__members__.values(), cls.__members__.keys()))[data]]
            else:
                raise ValueError('Value {value} not found for enum {cls}.'.format(value=repr(data), cls=cls.__name__))
        elif isinstance(data, str):
            if data.upper() in cls.__members__.keys():
                return cls.__members__[data.upper()]
            else:
                raise KeyError('Key {key} not found for enum {cls}.'.format(key=repr(data), cls=cls.__name__))
        else:
            raise TypeError('Data should be an int, str or {cls}, but {actual} found.'.format(
                cls=cls.__name__, actual=type(data).__name__,
            ))


class Plantuml(metaclass=ABCMeta):
    def __init__(self):
        """
        """
        pass

    @classmethod
    def autoload(cls, *args, **kwargs):
        """
        Autoload plantuml object from given arguments
        :return: auto-loaded plantuml object
        """
        raise NotImplementedError

    @classmethod
    def _check_version(cls, version: str):
        pass

    @abstractmethod
    def _get_version(self) -> str:
        raise NotImplementedError

    @property
    def version(self) -> str:
        """
        Get version information from this plantuml
        :return: version information
        """
        _version = self._get_version()
        self._check_version(_version)
        return _version

    def _check(self):
        self._check_version(self._get_version())

    def check(self) -> None:
        """
        Check this plantuml is okay or not, raise exception when not ok
        """
        return self._check()

    @check_func(keep_return=False)
    def test(self) -> bool:
        """
        Test this plantuml is okay or not
        :return: True if is okay, otherwise False
        """
        self._check()
        return True

    @abstractmethod
    def _generate_uml_data(self, type_: PlantumlResourceType, code: str) -> bytes:
        raise NotImplementedError

    def dump(self, path: str, type_: Union[int, str, PlantumlResourceType], code: str):
        """
        Dump uml data to file
        :param path: file path
        :param type_: resource type
        :param code: source code
        """
        save_binary_file(path, self._generate_uml_data(PlantumlResourceType.load(type_), code))

    def dump_binary(self, type_: Union[int, str, PlantumlResourceType], code: str) -> bytes:
        """
        Dump uml data to bytes
        :param type_: resource type
        :param code: source code
        """
        return self._generate_uml_data(PlantumlResourceType.load(type_), code)

    def dump_txt(self, code: str) -> str:
        """
        Dump txt uml data to str
        :param code: source code
        :return: txt uml data
        """
        return auto_decode(self._generate_uml_data(PlantumlResourceType.TXT, code))

    def _properties(self) -> Mapping[str, Any]:
        return {}

    def __repr__(self):
        return '<{cls} {properties}>'.format(
            cls=self.__class__.__name__,
            properties=', '.join(['{key}: {value}'.format(key=key, value=repr(value))
                                  for key, value in sorted(self._properties().items())]),
        )


_Tp = TypeVar('_Tp', bound=Plantuml)


def try_plantuml(cls: Type[_Tp], *args, **kwargs) -> Tuple[bool, Union[Optional[_Tp], Exception]]:
    """
    Try initialize plantuml object
    :param cls: plantuml class
    :param args: arguments
    :param kwargs: key-word arguments
    :return: (True, Plantuml) when success and (False, Exception) when failed
    """
    try:
        return True, cls.autoload(*args, **kwargs)
    except Exception as e:
        return False, e
