import string
import random
import json
import yaml
from os.path import join, expanduser, isdir
from os import mkdir
from shutil import rmtree

_tool_dir = join(expanduser('~'), '.kraken')
_tmp_dir = join(_tool_dir, 'tmp')
_used_names = []


def make_tmp_dir():
    """ Creates tmp directory in app home dir

    :return:
    """
    if not isdir(_tool_dir):
        mkdir(_tool_dir, 0o700)

    if not isdir(_tmp_dir):
        mkdir(_tmp_dir, 0o700)


def cleanup_tmp():
    """ Cleanup app tmp directory

    :return:
    """
    make_tmp_dir()
    rmtree(_tmp_dir, True)
    mkdir(_tmp_dir, 0o700)


def tmp_file(suffix=None) -> str:
    """ Returns unique name for temporary file.
    Name is guaranteed to be unique during app lifetime

    Example:
        with open(tmp.tmp_file(), 'w+') as f:
            f.write('your data')

    :param suffix: Suffix to append to generated file name
    :return:
    """
    global _used_names

    srand = random.SystemRandom()

    while True:
        rand_name = ''.join(srand.choice(string.ascii_letters + string.digits) for _ in range(12))
        rand_suff = ''.join(srand.choice(string.ascii_letters + string.digits) for _ in range(6))
        candidate = join(_tmp_dir, f'{rand_name}-{rand_suff}{suffix or ""}')

        if candidate not in _used_names:
            break

    _used_names.append(candidate)
    return candidate


def _serialize(data, stype):
    if stype == 'json':
        return json.dumps(data)
    elif stype == 'yaml':
        return yaml.dump(data, Dumper=yaml.SafeDumper)

    raise TypeError(f'unknown serializer {stype}')


def write_tmp(content, suffix=None, serializer='yaml') -> str:
    """ Write provided data to tmp file.
    Returns path to this file

    :param content:
    :param suffix:
    :return:
    :param suffix: file suffix
    :param serializer: which encoding method to use for non-string data. [json, yaml]
    :return: path to created file
    """
    name = tmp_file(suffix)

    if type(content) not in (str, bytes):
        content = _serialize(content, serializer)

    with open(name, 'w+') as f:
        f.write(content)

    return name
