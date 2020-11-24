from typing import Union, Tuple

import click

from .base import _check_plantuml, _click_exception_with_exit_code
from ..models.remote import RemotePlantuml
from ..utils import load_text_file


def _additional_info_for_remote(plantuml: RemotePlantuml):
    click.echo('Remote host : {host}'.format(host=plantuml.host))


def _check_remote_plantuml(success: bool, plantuml: Union[RemotePlantuml, Exception]) -> bool:
    return _check_plantuml('remote', success, plantuml, _additional_info_for_remote)


def print_remote_check_info(success, plantuml: Union[RemotePlantuml, Exception]):
    _ok = _check_remote_plantuml(success, plantuml)
    if not _ok:
        raise _click_exception_with_exit_code('PlantumlNotFound', 'Remote plantuml not found.', -1)


def print_url(success: bool, plantuml: Union[RemotePlantuml, Exception], sources: Tuple[str]):
    if success:
        for source in sources:
            code = load_text_file(source)
            click.echo(plantuml.get_online_editor_url(code))
    else:
        raise plantuml
