from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from multiprocessing import cpu_count
from threading import Lock
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
    pool = ThreadPoolExecutor(max_workers=concurrency)

    _items = {index: item for index, item in enumerate(items)}
    _results, _errors = {}, []
    _post_lock = Lock()
    _max_post_id = 0
    _skipped = False

    def _work_func(index_: int, item_):
        nonlocal _post_lock, _max_post_id, _items, _results, _skipped
        if _skipped:
            return

        try:
            _ret = process(index_, item_)
        except Exception as e:
            _results[index_] = (False, e)
        else:
            _results[index_] = (True, _ret)

        with _post_lock:
            while _max_post_id in _results.keys():
                _success, _data = _results[_max_post_id]
                if _success:
                    if not _skipped:
                        post_process(_max_post_id, _items[_max_post_id], _data)
                else:
                    if skip_once_error:
                        _skipped = True
                    _errors.append((_max_post_id, _items[_max_post_id], _data))

                _max_post_id += 1

    _post_errors = []

    def _callback(task):
        if task.exception():
            _post_errors.append(task.exception())

    tasks = []
    for index, item in enumerate(items):
        _task = pool.submit(_work_func, index, item)
        _task.add_done_callback(_callback)
        tasks.append(_task)
    wait(tasks, return_when=ALL_COMPLETED)

    if _post_errors:
        raise _post_errors[0]

    if len(_errors) > 0:
        if skip_once_error:
            _, _, err = _errors[0]
            raise err
        else:
            (final_error_process or _default_final_error_process)(_errors)
