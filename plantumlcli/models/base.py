from abc import ABCMeta, abstractmethod

from ..utils import check_func


class Plantuml(metaclass=ABCMeta):
    @abstractmethod
    def _get_version(self) -> str:
        raise NotImplementedError

    @property
    def version(self) -> str:
        return self._get_version()

    def _check(self):
        pass

    check = _check
    test = check_func(keep_return=False)(_check)
