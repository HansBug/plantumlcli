import base64
import os
import re
import string
import zlib
from typing import Optional, Mapping, Any, Union, Tuple

import requests
from pyquery import PyQuery
from urlobject import URLObject

from .base import Plantuml, PlantumlResourceType, _has_cairosvg

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
        raise ValueError(f"Host should be present, but {host!r} found.")

    _host_url = _host_process(host)
    if _host_url.scheme not in ['http', 'https']:
        raise ValueError(f"Host's scheme should be http or https, but {_host_url.scheme!r} found.")


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

    def _is_official(self):
        return self.__host.hostname in ('plantuml.com', 'www.plantuml.com') and \
            len(self.__host.path.segments) > 0 and self.__host.path.segments[0] == 'plantuml'

    def _check_version(self, version: str):
        if not self._is_official():
            if (not version) or ("plantuml" not in version.lower()) or ("version" not in version.lower()):
                raise ValueError(f"Invalid version information from homepage - {version!r}.")

    def _check_type_supported(self, type_: PlantumlResourceType):
        if type_ == PlantumlResourceType.PDF:
            if not _has_cairosvg():
                if self._is_official():
                    raise ValueError(f'Resource type {type_!r} not supported for plantuml official '
                                     f'site - {self.__host!r}.')
                else:
                    if self._get_server_version() < (1, 2023):
                        raise ValueError(f'Resource type {type_!r} not supported for '
                                         f'plantuml server site lower than 1.2023 - {self._get_server_version()!r}.')

    def _get_version(self) -> str:
        if not self._is_official():
            r = self.__get_homepage()
            return PyQuery(r.content.decode()).find('#footer').text().strip()
        else:
            return 'Official Site'

    def _get_server_version(self) -> Tuple[int, int, int]:
        (major, year, v), = re.findall(r'version\s*(?P<major>\d)(?P<year>\d{4})(?P<v>\d{2})',
                                       self._get_version(), re.IGNORECASE)

        return int(major), int(year), int(v.lstrip('0') or '0')

    def __get_uml_path(self, type_: str, code: str):
        return f"{type_}/{self.__compress(code)}"

    def __get_uml_url(self, type_: str, code: str) -> str:
        return self.__request_url(self.__get_uml_path(type_, code))

    def __get_uml(self, type_: str, code: str) -> bytes:
        r = self.__request(self.__get_uml_path(type_, code))
        return r.content

    def _generate_uml_data(self, type_: PlantumlResourceType, code: str) -> bytes:
        if type_ == PlantumlResourceType.PDF and _has_cairosvg():
            import cairosvg

            binary = self.__get_uml(PlantumlResourceType.SVG.name.lower(), code)
            return cairosvg.svg2pdf(bytestring=binary)
        else:
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
