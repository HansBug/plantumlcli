from functools import wraps
from typing import Callable


def check_func(keep_return: bool = False):
    """
    Wrap the check function into boolean-return function

    Example:
    >>> @check_func(keep_return=True)
    >>> def func1(a: int):
    >>>     if a < 0:
    >>>         raise ValueError
    >>>     return a + 1
    >>>
    >>> func1(1)  # (True, 2)
    >>> func1(-1)  # (False, ValueError())

    >>> @check_func(keep_return=False)
    >>> def func2(a: int):
    >>>     if a < 0:
    >>>         raise ValueError
    >>>     return a + 1
    >>>
    >>> func2(1)  # True
    >>> func2(-1)  # False

    :param keep_return: keep return value or raised exception or not, default is False
    :return: decorated function
    """

    def _decorator(func: Callable) -> Callable:
        @wraps(func)
        def _new_func(*args, **kwargs):
            try:
                _ret = func(*args, **kwargs)
            except Exception as e:
                _success, _return = False, e
            else:
                _success, _return = True, _ret

            if keep_return:
                return _success, _return
            else:
                return _success

        return _new_func

    return _decorator
