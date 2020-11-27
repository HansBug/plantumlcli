import os

import pytest
from urlobject import URLObject

from plantumlcli.models.remote import OFFICIAL_PLANTUML_HOST, RemotePlantuml
from ..test import exist_func, mark_select


def _get_test_class(host: str):
    _common_condition = exist_func(host)

    class _TestModelsRemote:
        @classmethod
        def _get_plantuml(cls, host_addr: str) -> RemotePlantuml:
            return RemotePlantuml(host_addr)

        @classmethod
        def _get_auto_plantuml(cls) -> RemotePlantuml:
            return RemotePlantuml.autoload(host=host)

        @mark_select(_common_condition)
        def test_init(self):
            plantuml = self._get_plantuml(host)
            assert plantuml.host == host

        @mark_select(_common_condition)
        def test_init_invalid(self):
            with pytest.raises(ValueError):
                self._get_plantuml('')
            with pytest.raises(ValueError):
                self._get_plantuml(str(URLObject(host).with_scheme('socks5')))

    return _TestModelsRemote


class TestModelsRemoteDefault(_get_test_class(OFFICIAL_PLANTUML_HOST)):
    pass


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
