from typing import Callable, Any


def all_func(*funcs: Callable[[], Any], quick_fail: bool = True) -> Callable[[], bool]:
    def _func():
        _success = True
        for _item_func in funcs:
            _ret = not not _item_func()
            _success = _success and _ret
            if not _success and quick_fail:
                break

        return _success

    return _func
