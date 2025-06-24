import hashlib
import os
from typing import Tuple, Optional

import requests

from .exist_versions import KNOWN_VERSIONS
from ..utils import download_file, get_requests_session


def _get_plantuml_jar_info(version: str) -> Tuple[str, Optional[int], Optional[str]]:
    if version in KNOWN_VERSIONS:
        info = KNOWN_VERSIONS[version]
        return info['url'], info['content_length'], info['sha256']
    else:
        url = f'https://github.com/plantuml/plantuml/releases/download/v{version}/plantuml-{version}.jar'
        return url, None, None


def get_plantuml_jar_url(version: str) -> str:
    url, _, _ = _get_plantuml_jar_info(version)
    return url


PLANTUML_CACHE_DIR = os.environ.get(
    'PLANTUML_CACHE_DIR',
    os.path.join(os.path.expanduser('~'), '.cache', 'plantumlcli'),
)


def _get_file_sha256(filename: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            data = f.read(1 << 20)
            if not data:
                break
            sha256_hash.update(data)
    return sha256_hash.hexdigest()


def download_plantuml_jar_file(version: str, filename: str):
    url, size, sha256 = _get_plantuml_jar_info(version)
    if os.path.exists(filename) and (size is None or os.path.getsize(filename) == size) and \
            (sha256 is None or _get_file_sha256(filename) == sha256):
        # file already ready
        return

    try:
        download_file(
            url=url, filename=filename, expected_size=size,
            session=get_requests_session(use_random_ua=False),
        )
        if os.path.exists(filename) and sha256 is not None:
            actual_sha256 = _get_file_sha256(filename)
            if actual_sha256 != sha256:
                raise requests.exceptions.HTTPError(f"Downloaded file is not of expected sha256 hash, "
                                                    f"{sha256!r} expected but {actual_sha256!r} found.")

    except:
        os.remove(filename)
        raise


def get_plantuml_jar_file(version: str) -> str:
    filename = os.path.join(PLANTUML_CACHE_DIR, 'jars', f'{version}', f'plantuml-{version}.jar')
    if os.path.dirname(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    download_plantuml_jar_file(version=version, filename=filename)
    return filename
