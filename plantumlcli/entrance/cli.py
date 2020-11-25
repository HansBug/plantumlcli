from typing import Optional, Tuple

import click
from click import Context, Option

from .general import _get_check_type, print_check_info, print_text_graph
from .remote import print_url, print_homepage_url
from ..config.meta import __TITLE__, __VERSION__, __AUTHOR__, __AUTHOR_EMAIL__
from ..models.base import try_plantuml, PlantumlResourceType
from ..models.local import LocalPlantuml, PLANTUML_JAR_ENV, find_java_from_env
from ..models.remote import OFFICIAL_PLANTUML_HOST, PLANTUML_HOST_ENV, RemotePlantuml


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
@click.option('--homepage-url', is_flag=True, help='Print url of remote plantuml editor.')
@click.option('-t', '--type', 'resource_type', default=PlantumlResourceType.TXT.name,
              type=click.Choice(PlantumlResourceType.__members__.keys(), case_sensitive=False),
              help='Type of plantuml resource.', show_default=True)
@click.option('-T', '--text', is_flag=True, help='Display text uml graph by stdout.')
@click.argument('sources', nargs=-1, type=click.Path(exists=True, dir_okay=False, readable=True))
def cli(java: str, plantuml: Optional[str], remote_host: str,
        check: bool, check_local: bool, check_remote: bool,
        url: bool, homepage_url: bool,
        resource_type: str, text: bool,
        sources: Tuple[str]):
    _local_ok, _local = try_plantuml(LocalPlantuml, java=java, plantuml=plantuml)
    _remote_ok, _remote = try_plantuml(RemotePlantuml, host=remote_host)

    if check or check_local or check_remote:  # check plantuml environment
        print_check_info(
            _get_check_type(check, check_local, check_remote),
            _local_ok, _local, _remote_ok, _remote
        )
    elif url or homepage_url:  # print url of remote plantuml
        if homepage_url:
            print_homepage_url(_remote_ok, _remote, sources)
        else:
            print_url(_remote_ok, _remote, sources, PlantumlResourceType.load(resource_type))
    else:
        if _local_ok:
            plantuml = _local
        else:
            plantuml = _remote

        if text:  # print text graph
            print_text_graph(plantuml, sources)
        else:
            print(sources)
            print(_local_ok, _local)
            print(_remote_ok, _remote)
