from multiprocessing import cpu_count
from typing import Union, Optional, Callable, TypeVar

import click

from ..models import Plantuml
from ..utils import timing_func

_DEFAULT_CONCURRENCY = cpu_count()


def _click_exception_with_exit_code(name: str, message: str, exitcode: int):
    class _ClickException(click.ClickException):
        exit_code = exitcode

    return type(name, (_ClickException,), {})(message)


_Tp = TypeVar('_Tp', bound=Plantuml)


@timing_func(keep_return=True)
def _plantuml_version(plantuml: _Tp):
    return plantuml.version


def _check_plantuml(name: str, success, plantuml: Union[_Tp, Exception],
                    callback: Optional[Callable[[_Tp, float], None]] = None) -> bool:
    _duration, _version = 0.0, None
    if success:
        try:
            _duration, _version = _plantuml_version(plantuml)
        except Exception as e:
            success, plantuml = False, e

    if success:
        click.secho('{name} plantuml detected.'.format(name=name.capitalize()), fg='green')

        click.echo(_version)
        if callback:
            callback(plantuml, _duration)
    else:
        click.secho('{name} plantuml not detected or has problem.'.format(name=name.capitalize()), fg='red')
        click.echo('Error : {error}'.format(error=repr(plantuml)))

    return success
