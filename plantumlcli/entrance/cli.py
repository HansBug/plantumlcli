from typing import Union, Optional, Tuple

import click
from click.core import Context, Option

from .base import _DEFAULT_CONCURRENCY
from .general import print_check_info, print_text_graph, process_plantuml, PlantumlCheckType
from .remote import print_url, print_homepage_url
from ..config.meta import __TITLE__, __VERSION__, __AUTHOR__, __AUTHOR_EMAIL__
from ..models.base import try_plantuml, PlantumlResourceType, Plantuml
from ..models.local import LocalPlantuml, find_java_from_env, PLANTUML_JAR_ENV
from ..models.remote import RemotePlantuml, PLANTUML_HOST_ENV, OFFICIAL_PLANTUML_HOST


def _select_plantuml(
        local_ok: bool, local: Union[LocalPlantuml, Exception],
        remote_ok: bool, remote: Union[RemotePlantuml, Exception],
        use_local: bool, use_remote: bool) -> Plantuml:
    if use_local:
        plantuml = local
    elif use_remote:
        plantuml = remote
    else:
        if local_ok:
            plantuml = local
        elif remote_ok:
            plantuml = remote
        else:
            plantuml = RuntimeError('No plantuml available.')

    if isinstance(plantuml, Plantuml):
        return plantuml
    else:
        raise plantuml


# noinspection PyUnusedLocal
def print_version(ctx: Context, param: Option, value: bool) -> None:
    """
    Print version information of cli
    :param ctx: click context
    :param param: current parameter's metadata
    :param value: value of current parameter
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo('{title}, version {version}.'.format(title=__TITLE__.capitalize(), version=__VERSION__))
    click.echo('Developed by {author}, {email}.'.format(author=__AUTHOR__, email=__AUTHOR_EMAIL__))
    ctx.exit()


# noinspection PyUnusedLocal
def validate_concurrency(ctx: Context, param: Option, value: int):
    if value > 0:
        return value
    else:
        raise ValueError("Concurrency should be no less than 1.")


CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Show package's version information.")
@click.option('-j', '--java', type=str, default=find_java_from_env(),
              help='Path of java executable file (will load from environment when not given).',
              show_default='java from ${PATH}')
@click.option('-p', '--plantuml', envvar=PLANTUML_JAR_ENV, type=str, default=None,
              help='Path of plantuml jar file (will load from ${{{env}}} when not given).'.format(
                  env=PLANTUML_JAR_ENV))
@click.option('-r', '--remote-host', envvar=PLANTUML_HOST_ENV, type=str, default=OFFICIAL_PLANTUML_HOST,
              help='Remote host of the online plantuml editor (will load from ${{{env}}} when not given).'.format(
                  env=PLANTUML_HOST_ENV),
              show_default=True)
@click.option('-L', '--use-local', is_flag=True, help='Use local plantuml only.')
@click.option('-R', '--use-remote', is_flag=True, help='Use remote plantuml only.')
@click.option('-c', '--check', is_flag=True, help='Check usable plantuml.')
@click.option('-u', '--url', is_flag=True, help='Print url of remote plantuml resource (ignore -L and -R).')
@click.option('--homepage-url', is_flag=True, help='Print url of remote plantuml editor (ignore -L, -R and -u).')
@click.option('-t', '--type', 'resource_type', default=PlantumlResourceType.PNG.name,
              type=click.Choice(PlantumlResourceType.__members__.keys(), case_sensitive=False),
              help='Type of plantuml resource.', show_default=True)
@click.option('-T', '--text', is_flag=True, help='Display text uml graph by stdout (ignore -t).')
@click.option('-o', '--output', type=str, multiple=True,
              help='Paths of output files (relative path supported, based on output dir in -O).')
@click.option('-O', '--output-dir', type=click.Path(exists=True, file_okay=False, writable=True), default='.',
              help='Base path for outputting files.', show_default='current path')
@click.option('-n', '--concurrency', type=int, default=_DEFAULT_CONCURRENCY, callback=validate_concurrency,
              help='Concurrency when running plantuml.', show_default=True)
@click.argument('sources', nargs=-1, type=click.Path(exists=True, dir_okay=False, readable=True))
def cli(java: str, plantuml: Optional[str], remote_host: str,
        use_local: bool, use_remote: bool, check: bool,
        url: bool, homepage_url: bool,
        resource_type: str, text: bool, output: Tuple[str], output_dir: str,
        concurrency: Optional[int], sources: Tuple[str]):
    _local_ok, _local = try_plantuml(LocalPlantuml, java=java, plantuml=plantuml)
    _remote_ok, _remote = try_plantuml(RemotePlantuml, host=remote_host)

    if check:  # check plantuml environment
        if use_local:
            _check_type = PlantumlCheckType.LOCAL
        elif use_remote:
            _check_type = PlantumlCheckType.REMOTE
        else:
            _check_type = PlantumlCheckType.BOTH
        print_check_info(_check_type, _local_ok, _local, _remote_ok, _remote)
    elif url or homepage_url:  # print url of remote plantuml
        if homepage_url:
            print_homepage_url(_remote_ok, _remote, sources, concurrency)
        else:
            print_url(_remote_ok, _remote, sources, PlantumlResourceType.load(resource_type), concurrency)
    else:  # run plantuml process
        plantuml = _select_plantuml(_local_ok, _local, _remote_ok, _remote, use_local, use_remote)

        if text:  # print text graph
            print_text_graph(plantuml, sources, concurrency)
        else:  # dump plantuml resource (core feature)
            process_plantuml(plantuml, sources, output, output_dir,
                             PlantumlResourceType.load(resource_type), concurrency)
