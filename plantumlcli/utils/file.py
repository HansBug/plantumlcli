from pathlib import Path
from typing import Optional

import chardet

_DEFAULT_ENCODING = 'utf-8'


def load_binary_file(path: str) -> bytes:
    """
    Load binary data from given path
    :param path: file path
    :return: binary data
    """
    return Path(path).read_bytes()


def load_text_file(path: str, encoding: Optional[str] = None) -> str:
    """
    Load text data from given path
    :param path: file path
    :param encoding: data encoding
    :return: text data
    """
    _bytes = load_binary_file(path)
    encoding = encoding or chardet.detect(_bytes)['encoding'] or _DEFAULT_ENCODING
    return _bytes.decode(encoding)


def save_binary_file(path: str, data: bytes):
    """
    Save binary data to given path
    :param path: file path
    :param data: binary data
    """
    return Path(path).write_bytes(data)


def save_text_file(path: str, data: str, encoding: Optional[str] = None):
    """
    Save text data to given path
    :param path: file path
    :param data: text data
    :param encoding: data encoding
    """
    return save_binary_file(path, data.encode(encoding or _DEFAULT_ENCODING))
