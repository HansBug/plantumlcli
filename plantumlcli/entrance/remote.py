from typing import Union, Tuple

import click

from .base import _check_plantuml, _click_exception_with_exit_code
from ..models.base import PlantumlResourceType
from ..models.remote import RemotePlantuml
from ..utils import load_text_file


def _additional_info_for_remote(plantuml: RemotePlantuml, duration: float):
    click.echo('Remote host : {host}'.format(host=plantuml.host))
    click.echo('Connection time : {time}s'.format(time='%.3f' % (duration,)))


def _check_remote_plantuml(success: bool, plantuml: Union[RemotePlantuml, Exception]) -> bool:
    return _check_plantuml('remote', success, plantuml, _additional_info_for_remote)


def print_remote_check_info(success, plantuml: Union[RemotePlantuml, Exception]) -> None:
    """
    Check if remote plantuml is found and okay
    :param success: plantuml object initialize success or not
    :param plantuml: plantuml object or raised exception when initialize
    """
    _ok = _check_remote_plantuml(success, plantuml)
    if not _ok:
        raise _click_exception_with_exit_code('PlantumlNotFound', 'Remote plantuml not found.', -1)


def print_url(success: bool, plantuml: Union[RemotePlantuml, Exception], sources: Tuple[str],
              resource_type: PlantumlResourceType):
    """
    Print url of online resources in remote plantuml
    :param success: plantuml object initialize success or not
    :param plantuml: plantuml object or raised exception when initialize
    :param sources: source code files
    :param resource_type: type of resource
    """
    if success:
        for source in sources:
            click.echo(plantuml.get_url(resource_type, load_text_file(source)))
    else:
        raise plantuml


def print_homepage_url(success: bool, plantuml: Union[RemotePlantuml, Exception], sources: Tuple[str]):
    """
    Print url of online editor in remote plantuml
    :param success: plantuml object initialize success or not
    :param plantuml: plantuml object or raised exception when initialize
    :param sources: source code files
    """
    if success:
        for source in sources:
            click.echo(plantuml.get_homepage_url(load_text_file(source)))
    else:
        raise plantuml
