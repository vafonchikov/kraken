import click
from .commands import commands
from .utils.tmp import cleanup_tmp


@click.group()
def cli():
    cleanup_tmp()


for cm in commands:
    cli.add_command(cm)


def run_cli():
    cli()


if __name__ == '__main__':
    run_cli()
