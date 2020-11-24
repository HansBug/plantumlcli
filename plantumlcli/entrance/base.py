from typing import Union, Optional, Callable, TypeVar

import click

from plantumlcli.models import Plantuml


def _click_exception_with_exit_code(name: str, message: str, exitcode: int):
    class _ClickException(click.ClickException):
        exit_code = exitcode

    return type(name, (_ClickException,), {})(message)


_Tp = TypeVar('_Tp', bound=Plantuml)


def _check_plantuml(name: str, success, plantuml: Union[_Tp, Exception],
                    callback: Optional[Callable[[_Tp, ], None]] = None) -> bool:
    if success:
        click.secho('{name} plantuml found.'.format(name=name.capitalize()), fg='green')
        click.echo(plantuml.version)
        if callback:
            callback(plantuml)
    else:
        click.secho('{name} plantuml not found.'.format(name=name.capitalize()), fg='red')

    return success
