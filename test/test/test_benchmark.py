import os
import time

import pytest

from .mark import benchmark


@benchmark
class TestBenchmark:
    def test_time(self):
        time.sleep(1.0)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
