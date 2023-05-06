import os
import time

import pytest

from plantumlcli.utils import check_func, timing_func


@pytest.mark.unittest
class TestUtilsDecorator:
    def test_check_func(self):
        @check_func(keep_return=True)
        def func1(a: int):
            if a < 0:
                raise ValueError

            return a + 1

        assert func1(1) == (True, 2)
        _success, _err = func1(-1)
        assert not _success
        assert isinstance(_err, ValueError)

        @check_func(keep_return=False)
        def func2(a: int):
            if a < 0:
                raise ValueError
            return a + 1

        assert func2(1)
        assert not func2(-1)

    def test_timing_func(self):
        @timing_func(keep_return=True)
        def func1(duration: float):
            time.sleep(duration)
            return duration * 2

        _time, _return = func1(1.0)
        assert 0.8 < _time < 1.2
        assert _return == 2.0

        @timing_func(keep_return=False)
        def func2(duration: float):
            time.sleep(duration)
            return duration * 2

        assert 0.8 < func2(1.0) < 1.2


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
