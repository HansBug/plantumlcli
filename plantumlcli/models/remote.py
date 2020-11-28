import base64
import os
import string
import zlib
from typing import Optional, Mapping, Any, Union

import requests
from pyquery import PyQuery
from urlobject import URLObject

from .base import Plantuml, PlantumlResourceType

PLANTUML_HOST_ENV = 'PLANTUML_HOST'
OFFICIAL_PLANTUML_HOST = 'http://www.plantuml.com/plantuml'


def find_plantuml_host_from_env() -> Optional[None]:
    return os.environ.get(PLANTUML_HOST_ENV, None)


def find_plantuml_host(plantuml_host: Optional[str] = None) -> Optional[str]:
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
        """
        :param host: the given host
        :param kwargs: other arguments
        """
        Plantuml.__init__(self)

        self.__host = host
        _check_remote(self.__host)
        self.__host = _host_process(self.__host)

        self.__session = requests.session()
        self.__request_params = kwargs

    @classmethod
    def autoload(cls, host: Optional[str] = None, **kwargs) -> 'RemotePlantuml':
        """
        Autoload RemotePlantuml object from given host, system environments and official site
        :param host: the given host
        :param kwargs: other arguments
        :return: remote plantuml object
        """
        return RemotePlantuml(find_plantuml_host(host), **kwargs)

    @property
    def host(self) -> str:
        """
        Host of remote plantuml
        :return: host of remote plantuml
        """
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
    def _check_version(cls, version: str):
        if (not version) or ("plantuml" not in version.lower()) or ("version" not in version.lower()):
            raise ValueError("Invalid version information from homepage - {info}.".format(info=repr(version)))

    def _get_version(self) -> str:
        r = self.__get_homepage()
        return PyQuery(r.content.decode()).find('#footer').text().strip()

    def __get_uml_url(self, type_: str, code: str) -> str:
        return self.__request_url(os.path.join(type_, self.__compress(code)))

    def __get_uml(self, type_: str, code: str) -> bytes:
        r = self.__request(os.path.join(type_, self.__compress(code)))
        return r.content

    def _generate_uml_data(self, type_: PlantumlResourceType, code: str) -> bytes:
        return self.__get_uml(type_.name.lower(), code)

    def _generate_uml_url(self, type_: PlantumlResourceType, code: str) -> str:
        return self.__get_uml_url(type_.name.lower(), code)

    def get_url(self, type_: Union[int, str, PlantumlResourceType], code: str) -> str:
        """
        Get resource url for the source code
        :param type_: type of resource
        :param code: source code
        :return:  url of resource
        """
        return self._generate_uml_url(PlantumlResourceType.load(type_), code)

    def get_homepage_url(self, code: str) -> str:
        """
        Get homepage url for the source code
        :param code: source code
        :return: url of homepage
        """
        return self.__get_uml_url('uml', code)
