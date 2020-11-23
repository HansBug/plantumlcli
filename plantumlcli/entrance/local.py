import os
from typing import Optional

import where

from ..utils.decorator import check_func


def _find_java_from_local() -> Optional[str]:
    return where.first('java')


def _check_local(java: str, plantuml: str):
    if not java or not os.path.exists(java):
        raise FileNotFoundError('Java executable {exec} not found.'.format(exec=repr(java)))
    if not os.path.isfile(java):
        raise IsADirectoryError('Java executable {exec} is not a file.'.format(exec=repr(java)))
    if not os.access(java, os.X_OK):
        raise PermissionError('Java executable {exec} not executable.'.format(exec=repr(java)))

    if not plantuml or not os.path.exists(plantuml):
        raise FileNotFoundError('Plantuml jar file {jar} not found.'.format(jar=repr(plantuml)))
    if not os.path.isfile(plantuml):
        raise IsADirectoryError('Plantuml jar file {jar} is not a file.'.format(jar=repr(plantuml)))
    if not os.access(plantuml, os.R_OK):
        raise PermissionError('Plantuml jar file {jar} not readable.'.format(jar=repr(plantuml)))


_if_local_ok = check_func(keep_return=False)(_check_local)
