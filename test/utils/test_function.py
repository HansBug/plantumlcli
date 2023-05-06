import os

import pytest

from plantumlcli.utils import all_func


@pytest.mark.unittest
class TestUtilsFunction:
    def test_all_func(self):
        _func1_count, _func2_count = 0, 0

        def _func1():
            nonlocal _func1_count
            _func1_count += 1
            return True

        def _func2():
            nonlocal _func2_count
            _func2_count += 1
            return False

        assert not all_func(_func1, _func2)()
        assert (_func1_count, _func2_count) == (1, 1)

        assert not all_func(_func1, _func1, _func2, _func1)()
        assert (_func1_count, _func2_count) == (3, 2)

        assert not all_func(_func1, _func1, _func2, _func1, quick_fail=False)()
        assert (_func1_count, _func2_count) == (6, 3)

        assert all_func(_func1, _func1, lambda: not _func2())()
        assert (_func1_count, _func2_count) == (8, 4)

        assert all_func()()


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
