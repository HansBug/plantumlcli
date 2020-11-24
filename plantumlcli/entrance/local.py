from typing import Optional

import where


def _find_java_from_local() -> Optional[str]:
    return where.first('java')
