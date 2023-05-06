import os

import pytest

from plantumlcli.config.meta import __TITLE__


@pytest.mark.unittest
class TestConfigMeta:
    def test_title(self):
        assert __TITLE__ == 'plantumlcli'


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
