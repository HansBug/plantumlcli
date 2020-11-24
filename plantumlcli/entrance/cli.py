from typing import Optional, Tuple

import click
from click import Context, Option

from .base import _click_exception_with_exit_code
from .local import _check_local_plantuml, print_local_check_info
from .remote import print_url, _check_remote_plantuml, print_remote_check_info
from ..config.meta import __TITLE__, __VERSION__, __AUTHOR__, __AUTHOR_EMAIL__
from ..models.base import try_plantuml
from ..models.local import LocalPlantuml, PLANTUML_JAR_ENV, find_java_from_env
from ..models.remote import OFFICIAL_PLANTUML_HOST, PLANTUML_HOST_ENV, RemotePlantuml


# noinspection PyUnusedLocal
def print_version(ctx: Context, param: Option, value: bool):
    if not value or ctx.resilient_parsing:
        return
    click.echo('{title}, version {version}.'.format(title=__TITLE__.capitalize(), version=__VERSION__))
    click.echo('Developed by {author}, {email}.'.format(author=__AUTHOR__, email=__AUTHOR_EMAIL__))
    ctx.exit()


def print_check_info(local_ok: bool, local: LocalPlantuml,
                     remote_ok: bool, remote: RemotePlantuml):
    _local_ok = _check_local_plantuml(local_ok, local)
    _remote_ok = _check_remote_plantuml(remote_ok, remote)
    if not _local_ok and not _remote_ok:
        raise _click_exception_with_exit_code('PlantumlNotFound', 'Neither local nor remote plantuml is found.', -1)


CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Show package's version information.")
@click.option('-j', '--java', type=str, default=find_java_from_env(),
              help='Path of java executable file (will load from environment when not given).',
              show_default=not not find_java_from_env())
@click.option('-p', '--plantuml', envvar=PLANTUML_JAR_ENV, type=str, default=None,
              help='Path of plantuml jar file (will load from ${{{env}}} when not given).'.format(
                  env=PLANTUML_JAR_ENV))
@click.option('-r', '--remote-host', envvar=PLANTUML_HOST_ENV, type=str, default=OFFICIAL_PLANTUML_HOST,
              help='Remote host of the online plantuml editor (will load from ${{{env}}} when not given).'.format(
                  env=PLANTUML_HOST_ENV),
              show_default=True)
@click.option('-c', '--check', is_flag=True, help='Check usable plantuml.')
@click.option('--check-local', is_flag=True, help='Check local plantuml.')
@click.option('--check-remote', is_flag=True, help='Check remote plantuml.')
@click.option('-u', '--url', is_flag=True, help='Print url of remote plantuml resource.')
@click.argument('sources', nargs=-1, type=click.Path(exists=True, dir_okay=False, readable=True))
def cli(java: str, plantuml: Optional[str], remote_host: str,
        check: bool, check_local: bool, check_remote: bool,
        url: bool, sources: Tuple[str]):
    _local_ok, _local = try_plantuml(LocalPlantuml, java=java, plantuml=plantuml)
    _remote_ok, _remote = try_plantuml(RemotePlantuml, host=remote_host)

    if check_local:
        print_local_check_info(_local_ok, _local)
    elif check_remote:
        print_remote_check_info(_remote_ok, _remote)
    elif check:
        print_check_info(_local_ok, _local, _remote_ok, _remote)
    elif url:
        print_url(_remote_ok, _remote, sources)
    else:
        print(sources)
        print(_local_ok, _local)
        print(_remote_ok, _remote)
