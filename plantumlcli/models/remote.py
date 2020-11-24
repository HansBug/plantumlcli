import base64
import os
import string
import zlib
from typing import Optional, Mapping, Any

import requests
from pyquery import PyQuery
from urlobject import URLObject

from .base import Plantuml

PLANTUML_HOST_ENV = 'PLANTUML_HOST'
OFFICIAL_PLANTUML_HOST = 'http://www.plantuml.com/plantuml'


def find_plantuml_host_from_env() -> Optional[None]:
    return os.environ.get(PLANTUML_HOST_ENV, None)


def find_plantuml_host(plantuml_host: Optional[str]) -> Optional[str]:
    return plantuml_host or find_plantuml_host_from_env() or OFFICIAL_PLANTUML_HOST


_trans_from_base64_to_plantuml = bytes.maketrans(
    (string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/').encode(),
    (string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_').encode(),
)


def _host_process(host: str) -> URLObject:
    return URLObject(host).without_fragment().without_query()


def _check_remote(host: str):
    if not host:
        raise ValueError("Host should be present, but {actual} found.".format(actual=repr(host)))

    _host_url = _host_process(host)
    if _host_url.scheme not in ['http', 'https']:
        raise ValueError(
            "Host's scheme should be http or https, but {actual} found.".format(actual=repr(_host_url.scheme)))


class RemotePlantuml(Plantuml):
    __BYTE_TRANS = _trans_from_base64_to_plantuml

    def __init__(self, host: str, **kwargs):
        Plantuml.__init__(self)

        self.__host = host
        _check_remote(self.__host)
        self.__host = _host_process(self.__host)

        self.__session = requests.session()
        self.__request_params = kwargs
        self.__version = None

    @classmethod
    def autoload(cls, host: Optional[str] = None, **kwargs) -> 'RemotePlantuml':
        return RemotePlantuml(find_plantuml_host(host), **kwargs)

    @property
    def host(self) -> str:
        return str(self.__host)

    def _properties(self) -> Mapping[str, Any]:
        return {
            'host': str(self.__host),
        }

    @classmethod
    def __compress(cls, code: str) -> str:
        _compressed = zlib.compress(code.encode())[2:-4]
        return base64.b64encode(_compressed).translate(cls.__BYTE_TRANS).decode()

    def __request_url(self, path: str) -> str:
        return str(self.__host.add_path(path))

    def __request(self, path: str, stream: bool = False):
        r = self.__session.get(self.__request_url(path), stream=stream, **self.__request_params)
        r.raise_for_status()
        return r

    def __get_homepage(self):
        return self.__request('')

    @classmethod
    def __check_version(cls, version_info: str):
        if ("version" not in version_info) or ("plantuml server" not in version_info.lower()) or (not version_info):
            raise ValueError("Invalid version information from homepage - {info}.".format(info=repr(version_info)))

    def _get_version(self) -> str:
        if not self.__version:
            r = self.__get_homepage()
            _version = PyQuery(r.content.decode()).find('#footer').text().strip()
            self.__check_version(_version)
            self.__version = _version

        return self.__version

    def _check(self):
        self.__get_homepage()

    def __get_uml_url(self, type_: str, code: str) -> str:
        return self.__request_url(os.path.join(type_, self.__compress(code)))

    def __get_uml(self, type_: str, code: str) -> bytes:
        r = self.__request(os.path.join(type_, self.__compress(code)))
        return r.content

    def get_online_editor_url(self, code: str) -> str:
        return self.__get_uml_url('uml', code)

    def get_txt_uml_url(self, code: str) -> str:
        return self.__get_uml_url('txt', code)

    def get_txt_uml(self, code: str) -> str:
        return self.__get_uml('txt', code).decode()

    def get_png_uml_url(self, code: str) -> str:
        return self.__get_uml_url('png', code)

    def get_png_uml(self, code: str) -> bytes:
        return self.__get_uml('png', code)

    def get_svg_uml_url(self, code: str) -> str:
        return self.__get_uml_url('svg', code)

    def get_svg_uml(self, code: str) -> bytes:
        return self.__get_uml('svg', code)

    def get_eps_uml_url(self, code: str) -> str:
        return self.__get_uml_url('eps', code)

    def get_eps_uml(self, code: str) -> bytes:
        return self.__get_uml('eps', code)
