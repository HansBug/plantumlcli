from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import TypeVar, Type, Optional, Tuple, Union, Any, Mapping

from ..utils import check_func


class PlantumlType(IntEnum):
    LOCAL = 1
    REMOTE = 2


class Plantuml(metaclass=ABCMeta):
    def __init__(self):
        pass

    @classmethod
    def autoload(cls, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _get_version(self) -> str:
        raise NotImplementedError

    @property
    def version(self) -> str:
        return self._get_version()

    @abstractmethod
    def _check(self):
        raise NotImplementedError

    def check(self):
        return self._check()

    @check_func(keep_return=False)
    def test(self):
        return self._check()

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
    try:
        return True, cls.autoload(*args, **kwargs)
    except Exception as e:
        return False, e
