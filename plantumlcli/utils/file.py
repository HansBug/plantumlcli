from pathlib import Path
from typing import Optional

import chardet


def load_binary_file(path: str) -> bytes:
    return Path(path).read_bytes()


def load_text_file(path: str, encoding: Optional[str] = None) -> str:
    _bytes = load_binary_file(path)
    encoding = encoding or chardet.detect(_bytes)['encoding'] or 'utf-8'
    return _bytes.decode(encoding)
