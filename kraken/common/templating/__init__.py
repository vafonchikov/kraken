import jinja2
from .helpers import *


def render(template, context=None, base_dir=None, globals=None, **kwargs):
    """ Renders template with context in predefined environment.

    :param template:
    :param context:
    :param base_dir:
    :param globals: Template globals
    :param kwargs: extra arguments passed to jinja2 environment
    :return:
    """
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(base_dir), **kwargs)

    try:
        return env.from_string(template, globals=globals).render(context)
    except jinja2.TemplateNotFound as err:
        raise Exception(f'template not found: {err}')
    except jinja2.TemplateRuntimeError as err:
        raise Exception(f'template runtime error: {err}')
    except jinja2.TemplateError as err:
        raise Exception(f'template error: {err}')
