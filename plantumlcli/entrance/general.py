import os
from enum import IntEnum
from typing import Optional, Tuple, Union

import click
from requests.exceptions import BaseHTTPError, HTTPError

from .base import _click_exception_with_exit_code
from .local import _check_local_plantuml, print_local_check_info
from .remote import _check_remote_plantuml, print_remote_check_info
from ..models.base import PlantumlType, Plantuml, PlantumlResourceType
from ..models.local import LocalPlantuml, LocalPlantumlExecuteError
from ..models.remote import RemotePlantuml
from ..utils import load_text_file, linear_process, save_binary_file, auto_decode


def print_double_check_info(local_ok: bool, local: LocalPlantuml,
                            remote_ok: bool, remote: RemotePlantuml) -> None:
    """
    Check if remote and local plantuml is found and okay
    :param local_ok: local plantuml object initialize success or not
    :param local: local plantuml object or raised exception when initialize
    :param remote_ok: remote plantuml object initialize success or not
    :param remote: remote plantuml object or raised exception when initialize
    """
    _local_ok = _check_local_plantuml(local_ok, local)
    _remote_ok = _check_remote_plantuml(remote_ok, remote)
    if not _local_ok and not _remote_ok:
        raise _click_exception_with_exit_code('PlantumlNotFound', 'Neither local nor remote plantuml is found.', -1)


class PlantumlCheckType(IntEnum):
    LOCAL = PlantumlType.LOCAL.value
    REMOTE = PlantumlType.REMOTE.value
    BOTH = 3


def print_check_info(check_type: PlantumlCheckType,
                     local_ok: bool, local: LocalPlantuml,
                     remote_ok: bool, remote: RemotePlantuml) -> None:
    """
    Check for all the situations of plantuml
    :param check_type: type of checking process (BOTH, LOCAL and REMOTE)
    :param local_ok: local plantuml object initialize success or not
    :param local: local plantuml object or raised exception when initialize
    :param remote_ok: remote plantuml object initialize success or not
    :param remote: remote plantuml object or raised exception when initialize
    """
    if check_type == PlantumlCheckType.BOTH:
        print_double_check_info(local_ok, local, remote_ok, remote)
    elif check_type == PlantumlCheckType.LOCAL:
        print_local_check_info(local_ok, local)
    elif check_type == PlantumlCheckType.REMOTE:
        print_remote_check_info(remote_ok, remote)
    else:
        # nothing to check, maybe warnings can be placed here.
        pass


def print_text_graph(plantuml: Plantuml, sources: Tuple[str], concurrency: int):
    """
    Print text graph of source codes
    :param plantuml: plantuml object
    :param sources: source code files
    :param concurrency: concurrency when running this
    """
    _error_count = 0

    def _process_text(src: str):
        try:
            return True, plantuml.dump_txt(load_text_file(src))
        except (LocalPlantumlExecuteError, OSError, BaseHTTPError, HTTPError) as e:
            return False, e

    def _print_text(src: str, ret: Tuple[bool, Union[str, LocalPlantumlExecuteError]]):
        _success, _data = ret

        if _success:
            click.secho('{source}: '.format(source=src), fg='green')
            click.echo(_data)
        else:
            nonlocal _error_count
            if isinstance(_data, LocalPlantumlExecuteError):
                click.secho('{source}: [error with exitcode {code}]'.format(source=src, code=_data.exitcode), fg='red')
                click.secho(_data.stderr, fg='red')
            else:
                if hasattr(_data, 'response'):
                    response = getattr(_data, 'response')
                    if hasattr(response, 'status_code'):
                        code = getattr(response, 'status_code')
                    else:
                        code = None
                else:
                    response, code = None, None

                if code:
                    click.secho('{source}: [{cls} {code}]'.format(
                        source=src, cls=type(_data).__name__, code=code), fg='red')
                else:
                    click.secho('{source}: [{cls}]'.format(source=src, cls=type(_data).__name__), fg='red')

                click.secho(str(_data), fg='red')
                if response is not None and code and response.content:
                    click.secho(auto_decode(response.content), fg='red')
                click.secho('', fg='red')

            _error_count += 1

    linear_process(
        items=sources,
        process=lambda i, src: _process_text(src),
        post_process=lambda i, src, ret: _print_text(src, ret),
        concurrency=concurrency,
    )

    if _error_count > 0:
        raise _click_exception_with_exit_code(
            name='TextGraphError',
            message='{count} error(s) found when generating text graph.'.format(count=_error_count),
            exitcode=-2,
        )


def process_plantuml(plantuml: Plantuml, sources: Tuple[str],
                     outputs: Tuple[str], output_dir: Optional[str],
                     type_: PlantumlResourceType, concurrency: int):
    if outputs and len(outputs) != len(sources):
        raise ValueError('Amount of output file(s) should be {expect}, but {actual} found.'
                         .format(expect=len(sources), actual=len(outputs)))

    def _output_filename(index: int):
        if outputs:
            name = outputs[index]
        else:
            _, _filename = os.path.split(sources[index])
            _name, _ = os.path.splitext(_filename)
            name = '{name}.{ext}'.format(name=_name, ext=type_.name.lower())
        return os.path.join(output_dir or os.curdir, name)

    def _process_code(index: int):
        return plantuml.dump_binary(type_, load_text_file(sources[index]))

    def _post_process_data(index: int, ret: bytes):
        save_binary_file(_output_filename(index), ret)

    linear_process(
        items=sources,
        process=lambda i, src: _process_code(i),
        post_process=lambda i, src, ret: _post_process_data(i, ret),
        concurrency=concurrency,
    )
