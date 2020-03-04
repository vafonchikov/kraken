import click
from kraken.common.bootstrap import create_builder


@click.command()
@click.option('-d', '--dir', 'lookup_dir', default='.k8s',
              help='Directory where create configs')
@click.option('-V', '--version', default='v1',
              help='Config version to use')
def new(lookup_dir, version):
    """ Create new deployment configuration for project
    """
    builder = create_builder(version)
    builder.run(lookup_dir)
