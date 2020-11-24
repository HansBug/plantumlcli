from typing import Union, Tuple

import click

from ..models.remote import RemotePlantuml
from ..utils import check_func, load_text_file


def _check_remote(host: str):
    RemotePlantuml(host).check()


_if_remote_ok = check_func(keep_return=False)(_check_remote)


def print_url(success: bool, plantuml: Union[RemotePlantuml, Exception], sources: Tuple[str]):
    if success:
        for source in sources:
            code = load_text_file(source)
            click.echo(plantuml.get_online_editor_url(code))
    else:
        raise plantuml
