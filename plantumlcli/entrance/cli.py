from typing import Optional

import click
from click import Context, Option

from .local import _find_java_from_local, _if_local_ok
from .remote import _if_remote_ok
from ..config.meta import __TITLE__, __VERSION__, __AUTHOR__, __AUTHOR_EMAIL__
from ..models.remote import OFFICIAL_PLANTUML_HOST


# noinspection PyUnusedLocal
def print_version(ctx: Context, param: Option, value: bool):
    if not value or ctx.resilient_parsing:
        return
    click.echo('{title}, version {version}.'.format(title=__TITLE__.capitalize(), version=__VERSION__))
    click.echo('Developed by {author}, {email}.'.format(author=__AUTHOR__, email=__AUTHOR_EMAIL__))
    ctx.exit()


CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Show package's version information.")
@click.option('-j', '--java', envvar='JAVA_EXEC', type=str, default=lambda: _find_java_from_local())
@click.option('-p', '--plantuml', envvar='PLANTUML_JAR', type=str, default=None)
@click.option('-h', '--remote-host', envvar='PLANTUML_HOST', type=str, default=OFFICIAL_PLANTUML_HOST)
def cli(java: str, plantuml: Optional[str], remote_host: str):
    if _if_local_ok(java, plantuml):
        print(java, plantuml)
    elif _if_remote_ok(remote_host):
        print(remote_host)
    else:
        raise RuntimeError
