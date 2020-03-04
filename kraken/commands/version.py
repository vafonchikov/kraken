import click
import kraken


@click.command()
def version():
    """ Display tool version
    """
    print(f'''Kraken deployment tool

Version: {kraken.__version__}''')
