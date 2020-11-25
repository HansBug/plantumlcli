from pathlib import Path
from typing import Optional

from .encoding import auto_decode, _DEFAULT_ENCODING


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
    return auto_decode(load_binary_file(path), encoding)


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
