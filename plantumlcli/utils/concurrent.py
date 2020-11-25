from multiprocessing import cpu_count, Lock
from multiprocessing.pool import ThreadPool
from typing import Iterable, TypeVar, Callable, Optional, List, Tuple

_Ti = TypeVar('_Ti')
_Tr = TypeVar('_Tr')


def _default_final_error_process(errors: List[Tuple[int, _Ti, Exception]]):
    _, _, err = errors[0]
    raise err


def linear_process(items: Iterable[_Ti],
                   process: Callable[[int, _Ti], _Tr],
                   post_process: Callable[[int, _Ti, _Tr], None],
                   concurrency: int = None,
                   skip_once_error: bool = True,
                   final_error_process: Optional[Callable[[List[Tuple[int, _Ti, Exception]]], None]] = None):
    concurrency = concurrency or cpu_count()
    pool = ThreadPool(processes=concurrency)

    _post_lock = Lock()
    _max_post_id = 0
    _items, _result, _errors = {}, {}, []
    _skipped = False
    for index, item in enumerate(items):
        _items[index] = item

        def _func():
            nonlocal _skipped, _max_post_id
            if _skipped:
                return

            try:
                _ret = process(index, item)
            except Exception as e:
                _result[index] = (False, e)
            else:
                _result[index] = (True, _ret)

            with _post_lock:
                while _max_post_id in _result.keys():
                    _success, _data = _result[_max_post_id]
                    if _success:
                        if not _skipped:
                            post_process(_max_post_id, _items[_max_post_id], _data)
                    else:
                        if skip_once_error:
                            _skipped = True
                        _errors.append((_max_post_id, _items[_max_post_id], _data))

                    _max_post_id += 1

        if not _skipped:
            pool.apply(func=_func, )

    pool.close()
    pool.join()

    if len(_errors) > 0:
        if skip_once_error:
            _, _, err = _errors[0]
            raise err
        else:
            (final_error_process or _default_final_error_process)(_errors)
