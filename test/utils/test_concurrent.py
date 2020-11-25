import os
import time

import pytest

from plantumlcli.utils import linear_process, timing_func
from ..test import unittest


@unittest
class TestUtilsConcurrent:
    def test_linear_process(self):
        for _ in range(0, 1000):
            _list = []
            linear_process(
                items=[2, 3, 5, 7],
                process=lambda i, x: x * x,
                post_process=lambda i, x, r: _list.append((i, x, r)),
                concurrency=4,
            )
            assert _list == [(0, 2, 4), (1, 3, 9), (2, 5, 25), (3, 7, 49)]

    def test_linear_process_concurrent(self):
        def _calc(x):
            time.sleep(0.5)
            return x * x

        def _func(concurrency: int):
            _list = []
            linear_process(
                items=[2, 3, 5, 7],
                process=lambda i, x: _calc(x),
                post_process=lambda i, x, r: _list.append((i, x, r)),
                concurrency=concurrency,
            )
            assert _list == [(0, 2, 4), (1, 3, 9), (2, 5, 25), (3, 7, 49)]

        @timing_func(keep_return=False)
        def _timing_1():
            _func(1)

        @timing_func(keep_return=False)
        def _timing_2():
            _func(2)

        @timing_func(keep_return=False)
        def _timing_4():
            _func(4)

        assert 1.7 < _timing_1() < 2.3
        assert 0.7 < _timing_2() < 1.3
        assert 0.2 < _timing_4() < 0.8


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
