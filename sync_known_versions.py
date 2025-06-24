import argparse
import hashlib
import os
import pathlib
from pprint import pformat
from typing import Dict

import requests
from hbutils.system import TemporaryDirectory
from natsort import natsorted
from tqdm import tqdm

from plantumlcli.utils import get_requests_session

github_versions = [
    "1.2025.3",
    "1.2025.2",
    "1.2025.1",
    "1.2025.0",
    "1.2024.8",
    "1.2024.7",
    "1.2024.6",
    "1.2024.5",
    "1.2024.4",
    "1.2024.3",
    "1.2024.2",
    "1.2024.1",
    "1.2024.0",
    "1.2023.13",
    "1.2023.12",
    "1.2023.11",
    "1.2023.10",
    "1.2023.9",
    "1.2023.8",
    "1.2023.7",
    "1.2023.6",
    "1.2023.5",
    "1.2023.4",
    "1.2023.3",
    "1.2023.2",
    "1.2023.1",
    "1.2023.0",
    "1.2022.14",
    "1.2022.13",
    "1.2022.12",
    "1.2022.11",
    "1.2022.10",
    "1.2022.9",
    "1.2022.8",
    "1.2022.7",
    "1.2022.6",
    "1.2022.5",
    "1.2022.4",
    "1.2022.3",
    "1.2022.2",
    "1.2022.1",
    "1.2022.0"
]

sourceforge_versions = [
    "1.2023.7",
    "1.2023.6",
    "1.2023.5",
    "1.2023.4",
    "1.2023.2",
    "1.2023.1",
    "1.2023.0",
    "1.2022.14",
    "1.2022.13",
    "1.2022.12",
    "1.2022.10",
    "1.2022.8",
    "1.2022.7",
    "1.2022.6",
    "1.2022.5",
    "1.2022.4",
    "1.2022.3",
    "1.2022.2",
    "1.2022.1",
    "1.2022.0",
    "1.2021.16",
    "1.2021.15",
    "1.2021.14",
    "1.2021.13",
    "1.2021.12",
    "1.2021.11",
    "1.2021.10",
    "1.2021.9",
    "1.2021.8",
    "1.2021.7",
    "1.2021.6",
    "1.2021.5",
    "1.2021.4",
    "1.2021.3",
    "1.2021.2",
    "1.2021.1",
    "1.2021.0",
    "1.2020.26",
    "1.2020.24",
    "1.2020.23",
    "1.2020.22",
    "1.2020.21",
    "1.2020.20",
    "1.2020.19",
    "1.2020.18",
    "1.2020.17",
    "1.2020.16",
    "1.2020.15",
    "1.2020.14",
    "1.2020.13",
    "1.2020.12",
    "1.2020.11",
    "1.2020.10",
    "1.2020.9",
    "1.2020.8",
    "1.2020.7",
    "1.2020.6",
    "1.2020.5",
    "1.2020.4",
    "1.2020.3",
    "1.2020.2",
    "1.2020.1",
    "1.2020.0",
    "1.2019.13",
    "1.2019.12",
    "1.2019.11",
    "1.2019.10",
    "1.2019.9",
    "1.2019.8",
    "1.2019.7",
    "1.2019.6",
    "1.2019.5",
    "1.2019.4",
    "1.2019.3",
    "1.2019.2",
    "1.2019.1",
    "1.2019.0",
    "1.2018.14",
    "1.2018.13",
    "1.2018.12",
    "1.2018.11",
    "1.2018.10",
    "1.2018.9",
    "1.2018.8",
    "1.2018.7",
    "1.2018.6",
    "1.2018.5",
    "1.2018.4",
    "1.2018.3",
    "1.2018.2",
    "1.2018.1",
    "1.2018.0",
    "1.2017.20",
    "1.2017.19",
    "1.2017.18",
    "1.2017.16",
    "1.2017.15",
    "1.2017.14",
    "1.2017.13",
    "1.2017.12"
]


def download_file(url, filename, expected_size: int = None, desc=None, session=None, silent: bool = False, **kwargs):
    session = session or get_requests_session()
    response = session.get(url, stream=True, allow_redirects=True, **kwargs)
    expected_size = expected_size or response.headers.get('Content-Length', None)
    expected_size = int(expected_size) if expected_size is not None else expected_size

    desc = desc or os.path.basename(filename)
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(filename, 'wb') as f:
        with tqdm(total=expected_size, unit='B', unit_scale=True, unit_divisor=1024, desc=desc, disable=silent) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
                pbar.update(len(chunk))

    actual_size = os.path.getsize(filename)
    if expected_size is not None and actual_size != expected_size:
        os.remove(filename)
        raise requests.exceptions.HTTPError(f"Downloaded file is not of expected size, "
                                            f"{expected_size} expected but {actual_size} found.")

    return filename


def _get_version_info(version: str, url: str, session=None):
    session = session or get_requests_session()
    resp = session.head(url, allow_redirects=True)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()

    with TemporaryDirectory() as td:
        filename = os.path.join(td, f'plantuml-{version}.jar')
        download_file(url, filename, session=session)
        sha256_hash = hashlib.sha256()
        with open(filename, "rb") as f:
            while True:
                data = f.read(1 << 20)
                if not data:
                    break
                sha256_hash.update(data)
        sha256_result = sha256_hash.hexdigest()

    return {
        'version': version,
        'version_tuple': tuple(map(int, version.split('.'))),
        'url': url,
        'content_length': int(resp.headers['Content-Length']),
        'sha256': sha256_result,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update known version information')
    parser.add_argument('-o', '--output_file', required=True, help='Output files of known versions')
    parser.add_argument('-n', '--count', default=20, help='Run count of this time')

    args = parser.parse_args()
    session = get_requests_session()

    dst_file = args.output_file
    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
    if os.path.exists(dst_file):
        exec(pathlib.Path(dst_file).read_text())
        known_versions: Dict[str, dict] = vars()['KNOWN_VERSIONS']
    else:
        known_versions: Dict[str, dict] = {}

    cnt = 0
    max_count = args.count
    for version in tqdm(sourceforge_versions[::-1]):
        if cnt >= max_count:
            break
        if version in known_versions:
            continue
        url = f'https://sourceforge.net/projects/plantuml/files/{version}/plantuml.{version}.jar/download'
        _info = _get_version_info(version, url, session=session)
        if not _info:
            continue
        known_versions[version] = _info
        cnt += 1

    for version in tqdm(github_versions[::-1]):
        if cnt >= max_count:
            break
        if version in known_versions:
            continue
        url = f'https://github.com/plantuml/plantuml/releases/download/v{version}/plantuml-{version}.jar'
        _info = _get_version_info(version, url, session=session)
        if not _info:
            continue
        known_versions[version] = _info
        cnt += 1

    known_versions = dict(natsorted(known_versions.items()))
    with open(dst_file, 'w') as f:
        print(f'KNOWN_VERSIONS = {pformat(known_versions, sort_dicts=False)}', file=f)
