import click
from kraken.common.app_config import read_configs
from kraken.common.app_config.schema import set_condition
from kraken.common.image_build import img_build_docker
from kraken.utils.cli import click_kv_option_parser


@click.command()
@click.option('-d', '--dir', 'lookup_dir', default='.k8s',
              help='Directory where to look for configs. Default %(default)s')
@click.option('-s', '--set', 'set_vars', multiple=True, callback=click_kv_option_parser,
              help='Additional context parameters in format KEY=VALUE for config substitution')
@click.option('-p', '--part', 'part', multiple=True, default=[],
              help='Choose container for build')
@click.option('-c', '--context', 'context', default=".",
              help='Custom context. Default "./"')
@click.option('--local', 'local', is_flag=True,
              help='Build image locally')
@click.option('--no-cache', 'no_cache', is_flag=True, default=False,
              help='Not used docker cache')
@click.option('--docker-socket', 'docker_socket', default='unix://var/run/docker.sock',
              help='Use custom docker socket')
@click.option('--arg', 'build_args', multiple=True, default=None, callback=click_kv_option_parser,
              help='Specifying build arguments')
@click.argument('configs', required=False, nargs=-1)
def build(lookup_dir, set_vars, configs, part, context, local, no_cache, docker_socket, build_args):
    """ Build and push docker image.

    Build all (or several if filtered) containers configured in base dir
    Default base dir '.k8s'

    \b
    Use next environment variables or set manually in interactive:
    1. DOCKER_REGISTRY_URL
    2. DOCKER_REGISTRY_USER_NAME
    3. DOCKER_REGISTRY_USER_EMAIL
    4. DOCKER_REGISTRY_USER_PASSWORD


    Example:

    \b
    # Build and push all containers
    $ kraken build

    \b
    # Only build all containers
    $ kraken build --local

    \b
    # Build and push all containers from specific config
    $ kraken build 0-app.yml
    $ kraken build app

    \b
    # Build and push specific container
    $ kraken build -p nginx app
    """
    set_condition('type', 'build')

    confs = read_configs(lookup_dir, configs, set_vars)

    for conf in confs:
        img_build_docker(conf.data, part, conf.filename, lookup_dir, context, local, no_cache, docker_socket, build_args)
