import click
import yaml
import io
from kraken.utils.cli import click_kv_option_parser
from kraken.common.app_config import read_configs
from kraken.common.k8s.templates import render_from_config
from kraken.common.k8s.kubec import apply


@click.command()
@click.option('-d', '--dir', 'lookup_dir', default='.k8s',
              help='Directory where to look for configs. Default %(default)s')
@click.option('-s', '--set', 'set_vars', multiple=True, callback=click_kv_option_parser,
              help='Additional context parameters in format KEY=VALUE for config substitution')
@click.option('-SV', '--server-validate', 'server_dry_run', is_flag=True, default=False,
              help='Validate config of k8s server instead of kubectl (server-dry-run)')
@click.option('-V', '--validate', 'validate', is_flag=True, default=False,
              help='Validate configs without applying changes (dry-run)')
@click.option('--no-batch', 'no_batch', is_flag=True, default=False,
              help='Execute apply for each config instead of batch apply')
@click.argument('configs', required=False, nargs=-1)
def deploy(lookup_dir, set_vars, server_dry_run, validate, no_batch, configs):
    """ Apply or validate deployment to k8s cluster.
    """
    confs = read_configs(lookup_dir, configs, set_vars)

    rendered = []

    for conf in confs:
        for filename, content in render_from_config(conf).items():
            rendered.append((filename, yaml.safe_dump(content)))

    if no_batch:
        for conf in rendered:
            click.secho(f'Applying {conf[0]} (dry-run={validate}, server-dry-run={server_dry_run})', fg='blue')

            if not apply(conf[1], validate, server_dry_run=server_dry_run, fallback_to_dry_run=True):
                click.secho('Apply failed', fg='red')
                exit(1)

            click.secho('Configuration applied!', fg='green')
    else:
        buffer = io.StringIO()

        for conf in rendered:
            buffer.write(f'---\n# {conf[0]}\n---\n{conf[1]}\n\n')

        click.secho(f'Applying whole deployment (dry-run={validate}, server-dry-run={server_dry_run})', fg='blue')

        buffer.seek(0)
        if not apply(buffer.read(), validate, server_dry_run=server_dry_run, fallback_to_dry_run=True):
            click.secho('Apply failed', fg='red')
            exit(1)

        click.secho('Configuration applied!', fg='green')
