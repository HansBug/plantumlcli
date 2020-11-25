from typing import Optional

import chardet

_DEFAULT_ENCODING = 'utf-8'


def auto_decode(data: bytes, encoding: Optional[str] = None) -> str:
    return data.decode(encoding or chardet.detect(data)['encoding'] or _DEFAULT_ENCODING)
