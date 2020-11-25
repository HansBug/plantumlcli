from typing import Callable

import pytest
from _pytest.mark.structures import MarkDecorator

unittest = pytest.mark.unittest
benchmark = pytest.mark.benchmark
ignore = pytest.mark.ignore


def mark_select(condition: Callable[[], bool], ok: MarkDecorator = unittest,
                failed: MarkDecorator = ignore) -> MarkDecorator:
    return ok if condition() else failed
