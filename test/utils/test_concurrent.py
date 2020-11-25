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

        assert 1.6 < _timing_1() < 2.4
        assert 0.6 < _timing_2() < 1.4
        assert 0.1 < _timing_4() < 0.9

    def test_linear_process_error_skip(self):
        def _process(x):
            if x == 5:
                raise ValueError('value error for this awesome_test, value is {v}'.format(v=x))
            else:
                return x * x

        _list = []
        with pytest.raises(ValueError) as e:
            linear_process(
                items=[2, 3, 5, 7],
                process=lambda i, x: _process(x),
                post_process=lambda i, x, r: _list.append((i, x, r)),
                concurrency=4,
                skip_once_error=True,
            )

        err = e.value
        assert isinstance(err, ValueError)
        assert 'awesome_test' in str(err)
        assert '5' in str(err)
        assert _list == [(0, 2, 4), (1, 3, 9)]

    def test_linear_process_error_not_skip(self):
        def _process(x):
            if x in [3, 7]:
                raise ValueError('value error for this awesome_test, value is {v}'.format(v=x))
            else:
                return x * x

        _list = []
        with pytest.raises(ValueError) as e:
            linear_process(
                items=[2, 3, 5, 7],
                process=lambda i, x: _process(x),
                post_process=lambda i, x, r: _list.append((i, x, r)),
                concurrency=4,
                skip_once_error=False,
            )

        err = e.value
        assert isinstance(err, ValueError)
        assert 'awesome_test' in str(err)
        assert '3' in str(err)
        assert _list == [(0, 2, 4), (2, 5, 25)]

        def _raise_last(errs):
            raise errs[-1][2]

        _list = []
        with pytest.raises(ValueError) as e:
            linear_process(
                items=[2, 3, 5, 7],
                process=lambda i, x: _process(x),
                post_process=lambda i, x, r: _list.append((i, x, r)),
                concurrency=4,
                skip_once_error=False,
                final_error_process=_raise_last,
            )

        err = e.value
        assert isinstance(err, ValueError)
        assert 'awesome_test' in str(err)
        assert '7' in str(err)
        assert _list == [(0, 2, 4), (2, 5, 25)]

    def test_linear_process_error_post(self):
        _list = []

        def _post_process(i, x, r):
            if x == 3:
                raise ValueError('value error for this awesome_test, value is {v}'.format(v=x))
            _list.append((i, x, r))

        with pytest.raises(ValueError) as e:
            linear_process(
                items=[2, 3, 5, 7],
                process=lambda i, x: x * x,
                post_process=_post_process,
                concurrency=4,
            )

        err = e.value
        assert isinstance(err, ValueError)
        assert 'awesome_test' in str(err)
        assert '3' in str(err)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
