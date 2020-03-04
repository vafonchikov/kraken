import click

def colorize(data, text_color):
    click.secho(data, fg=text_color)
