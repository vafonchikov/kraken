import sys
import click

_debug = False


def set_debug(value):
    """ Enables or disables output of debugging messages

    :param value:
    :return:
    """
    global _debug
    _debug = value


def debug(msg):
    """ Print debug message to stdout

    :param msg:
    :return:
    """
    if _debug:
        sys.stdout.write(f'{msg}\n')


def info(msg):
    """ Print info message to stdout

    :param msg:
    :return:
    """
    sys.stdout.write(f'{msg}\n')


def error(msg):
    """ Print out error message to stderr

    :param msg:
    :return:
    """
    sys.stderr.write(f'error: {msg}\n')


def abort(msg, exit_code=1):
    """ Print error message and terminate application

    :param msg:
    :param exit_code:
    :return:
    """
    error(msg)
    exit(exit_code)


def click_kv_option_parser(ctx, param, value):
    """ Helper method that should be used as click option `callback=` to parse
    KEY=VALUE arguments.

    Example:
        @click.option('-o', '--option_name', type=str, callback=click_kv_option_parser,
                      help='Option in KEY=VALUE format')

    :param ctx:
    :param param:
    :param value:
    :return: dictionary with parsed {key, value} pairs
    """
    if not value:
        return value

    if type(value) is str:
        value = [value]

    try:
        return dict(item.split('=', 2) for item in value)
    except ValueError:
        raise click.BadOptionUsage(param, 'invalid option format: missing option value', ctx)


def common_options(fn):
    """

    :param fn:
    :return:
    """
    def verbose_callback(ctx, param, value):
        set_debug(value)

    fn = click.option('-v', '--verbose', is_flag=True, default=False, callback=verbose_callback,
                      expose_value=False, help='Increase output verbosity')(fn)
    return fn

