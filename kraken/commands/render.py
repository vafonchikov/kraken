import click
import json
import yaml
from kraken.common.app_config import read_configs
from kraken.common.k8s.templates import render_from_config
from kraken.utils.cli import click_kv_option_parser


def print_formatted(data, out_format, pretty=True):
    if out_format == 'yaml':
        for (filename, file_data) in data:
            print('---')
            print('# ' + filename)
            print(yaml.dump(file_data, explicit_start=pretty))
    elif out_format == 'json':
        for (filename, file_data) in data:
            print('-- ' + filename.replace('yml', 'json'))
            print(json.dumps(file_data, ensure_ascii=False, indent=4 if pretty else None))
            print("")
    else:
        raise click.BadOptionUsage('out', f'unknown format {out_format}', None)


@click.command()
@click.option('-d', '--dir', 'lookup_dir', default='.k8s',
              help='Directory where to look for configs. Default ".k8s"')
@click.option('-t', '--target', default='template', type=click.Choice(['template', 'config']),
              help='Whether to render just application config or complete k8s template. Default "template"')
@click.option('-o', '--out', default='yaml', type=click.Choice(['json', 'yaml']),
              help='Output format. Could be either yaml or json. Default "yaml"')
@click.option('-s', '--set', 'set_vars', multiple=True, callback=click_kv_option_parser,
              help='Additional context parameters in format KEY=VALUE for config substitution')
@click.option('-j', '--just', multiple=True,
              help='Only when target=template: render only kinds which name partially matches provided value')
@click.option('--no-pretty', 'no_pretty', is_flag=True,
              help='Disable pretty printing of json/yaml')
@click.argument('configs', required=False, nargs=-1)
def render(lookup_dir, target, out, set_vars, just, no_pretty, configs):
    """ Render configs / k8s templates.

    Prints all (or several if filtered) configs or k8s templates in which all variables substituted with provided
    values (via ENV or values.yaml).

    Example usages:

    \b
    # Build and print all k8s templates
    $ kraken render

    \b
    # Build and print all configs
    $ kraken render -t config

    \b
    # Build and print templates that starts with 0-app or 1-ing
    $ kraken render 0-app 1-ing

    \b
    # Look for configs in custom directory
    $ kraken render -d /path/to/custom/dir

    \b
    # Print only namespaces from all configs
    $ kraken render -j namespace
    """
    confs = read_configs(lookup_dir, configs, set_vars)

    if target == 'config':
        print_formatted([(cnf.filename, cnf.data) for cnf in confs], out, not no_pretty)
    else:
        for conf in confs:
            print_formatted(render_from_config(conf, just).items(), out, not no_pretty)
