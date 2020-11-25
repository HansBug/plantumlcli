from multiprocessing import cpu_count, Lock
from multiprocessing.pool import ThreadPool
from typing import Iterable, TypeVar, Callable

_Ti = TypeVar('_Ti')
_Tr = TypeVar('_Tr')


def linear_process(items: Iterable[_Ti],
                   process: Callable[[int, _Ti], _Tr],
                   post_process: Callable[[int, _Ti, _Tr], None],
                   concurrency: int = None):
    concurrency = concurrency or cpu_count()
    pool = ThreadPool(processes=concurrency)

    _post_lock = Lock()
    _max_post_id = 0
    _items, _result = {}, {}
    for index, item in enumerate(items):
        _items[index] = item

        def _func():
            _result[index] = process(index, item)

            with _post_lock:
                nonlocal _max_post_id
                while _max_post_id in _result.keys():
                    post_process(_max_post_id, _items[_max_post_id], _result[_max_post_id])
                    _max_post_id += 1

        pool.apply(func=_func, )

    pool.close()
    pool.join()
