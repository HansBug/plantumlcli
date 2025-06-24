"""
PlantUML JAR File Management Module

This module provides functionality for downloading and managing PlantUML JAR files.
It handles version checking, downloading from official sources, caching, and verification
of downloaded files through SHA256 hash checking.

The module supports both known versions (with pre-defined information) and arbitrary
versions by constructing the appropriate download URLs.
"""

import hashlib
import os
from typing import Tuple, Optional

import requests

from .exist_versions import KNOWN_VERSIONS
from ..utils import download_file, get_requests_session


def _get_plantuml_jar_info(version: str) -> Tuple[str, Optional[int], Optional[str]]:
    """
    Get information about a PlantUML JAR file for a specific version.

    :param version: The PlantUML version string
    :type version: str

    :return: A tuple containing (download URL, content length, SHA256 hash)
    :rtype: Tuple[str, Optional[int], Optional[str]]

    If the version is in the known versions list, returns pre-defined information.
    Otherwise, constructs a GitHub release URL without size or hash information.
    """
    if version in KNOWN_VERSIONS:
        info = KNOWN_VERSIONS[version]
        return info['url'], info['content_length'], info['sha256']
    else:
        url = f'https://github.com/plantuml/plantuml/releases/download/v{version}/plantuml-{version}.jar'
        return url, None, None


def get_plantuml_jar_url(version: str) -> str:
    """
    Get the download URL for a specific PlantUML JAR version.

    :param version: The PlantUML version string
    :type version: str

    :return: The download URL for the JAR file
    :rtype: str

    Example::

        >>> get_plantuml_jar_url('1.2022.7')
        'https://github.com/plantuml/plantuml/releases/download/v1.2022.7/plantuml-1.2022.7.jar'
    """
    url, _, _ = _get_plantuml_jar_info(version)
    return url


PLANTUML_CACHE_DIR = os.environ.get(
    'PLANTUML_CACHE_DIR',
    os.path.join(os.path.expanduser('~'), '.cache', 'plantumlcli'),
)


def _get_file_sha256(filename: str) -> str:
    """
    Calculate the SHA256 hash of a file.

    :param filename: Path to the file to hash
    :type filename: str

    :return: The SHA256 hash as a hexadecimal string
    :rtype: str

    The function reads the file in chunks to efficiently handle large files.
    """
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            data = f.read(1 << 20)
            if not data:
                break
            sha256_hash.update(data)
    return sha256_hash.hexdigest()


def download_plantuml_jar_file(version: str, filename: str):
    """
    Download a PlantUML JAR file for a specific version.

    :param version: The PlantUML version string
    :type version: str
    :param filename: The target filename where the JAR will be saved
    :type filename: str

    :raises requests.exceptions.HTTPError: If the downloaded file's SHA256 hash doesn't match the expected value

    This function skips the download if the file already exists with the correct size and hash.
    If the download fails or the hash verification fails, the partially downloaded file is removed.
    """
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
    """
    Get the path to a PlantUML JAR file, downloading it if necessary.

    :param version: The PlantUML version string
    :type version: str

    :return: The path to the downloaded JAR file
    :rtype: str

    This function ensures the JAR file is available locally, downloading it if needed.
    It creates the necessary directory structure in the cache directory and returns
    the full path to the JAR file.

    Example::

        >>> jar_path = get_plantuml_jar_file('1.2022.7')
        >>> # jar_path will be something like '/home/user/.cache/plantumlcli/jars/1.2022.7/plantuml-1.2022.7.jar'
    """
    filename = os.path.join(PLANTUML_CACHE_DIR, 'jars', f'{version}', f'plantuml-{version}.jar')
    if os.path.dirname(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    download_plantuml_jar_file(version=version, filename=filename)
    return filename
