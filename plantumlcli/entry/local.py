import os
from typing import Union

import click

from plantumlcli import LocalPlantuml
from .base import _check_plantuml, _click_exception_with_exit_code


def _additional_info_for_local(plantuml: LocalPlantuml, duration: float):
    click.echo('Java executable : {path}'.format(path=os.path.abspath(plantuml.java)))
    click.echo('Plantuml jar : {path}'.format(path=os.path.abspath(plantuml.plantuml)))


def _check_local_plantuml(success, plantuml: Union[LocalPlantuml, Exception]) -> bool:
    return _check_plantuml('local', success, plantuml, _additional_info_for_local)


def print_local_check_info(success, plantuml: Union[LocalPlantuml, Exception]) -> None:
    """
    Check if local plantuml is found and okay
    :param success: plantuml object initialize success or not
    :param plantuml: plantuml object or raised exception when initialize
    """
    _ok = _check_local_plantuml(success, plantuml)
    if not _ok:
        raise _click_exception_with_exit_code('PlantumlNotFound', 'Local plantuml not found.', -1)
