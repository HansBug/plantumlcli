from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import TypeVar, Type, Optional, Tuple, Union, Any, Mapping

from ..utils import check_func


class PlantumlType(IntEnum):
    LOCAL = 1
    REMOTE = 2


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
