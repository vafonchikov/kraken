from .version import version
from .render import render
from .build import build
from .new import new
from .deploy import deploy

# Register all commands here
commands = [
    version,
    render,
    build,
    new,
    deploy
]
