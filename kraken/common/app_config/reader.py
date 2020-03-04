import yaml
from os import listdir
from os.path import join, isdir, isfile, splitext
from .schema import validate_config, format_errors
from .config import Config
from typing import List
from kraken.common.templating import render
from kraken.utils import cli, tmp, VariableMap


def read_configs(base_dir, file_filter=None, extra_vars=None):
    # type: (str, list, dict) -> List[Config]
    """ Read all (or several if ``file_filter`` set) configs from ``base_dir``.

    :param base_dir:
    :param file_filter:
    :param extra_vars:
    :return:
    """
    if not file_filter:
        file_filter = []

    if not extra_vars:
        extra_vars = {}

    if not isdir(base_dir):
        return cli.abort(f'basic directory {base_dir} does not exist')

    var_map = VariableMap()
    var_map.read_env()

    val_file = join(base_dir, 'values.yml')
    if isfile(val_file):
        try:
            var_map.read_yaml(val_file)
        except Exception as err:
            return cli.abort(f'failed to parse values.yaml: {err}')

    var_map.update(extra_vars)

    configs = [file for file in listdir(base_dir) if
               file.endswith('.yml') and not file.startswith('_') and file != 'values.yml' and (
                       not file_filter or any(x.lower() in file.lower() for x in file_filter))]

    glob_files = [file for file in listdir(base_dir) if file.endswith('.yml') and file.startswith('_')]

    # todo: this piece of code pretty ugly. refactoring required
    tpl_globs = {}
    for gfile in glob_files:
        glob_name, _ = splitext(gfile)
        try:
            with open(join(base_dir, gfile), 'r') as f:
                tpl_globs[glob_name] = render(f.read(), var_map.dict(), base_dir=base_dir)
        except Exception as err:
            return cli.abort(f'failed to render partial {gfile}\n{err}')

    parsed = []
    for config_file in configs:
        conf_path = join(base_dir, config_file)

        with open(conf_path, 'r') as f:
            conf_txt = f.read()

        try:
            rendered = render(conf_txt, var_map.dict(), base_dir=base_dir, globals=tpl_globs)
        except Exception as err:
            tmp_dump = tmp.write_tmp(conf_txt, '.yml')
            return cli.abort(f'failed to render file {config_file}:\n{err}\n\nfailed content written to {tmp_dump}')

        try:
            loaded = yaml.load(rendered, Loader=yaml.SafeLoader)
        except Exception as err:
            tmp_dump = tmp.write_tmp(rendered, '.yml')
            return cli.abort(
                f'failed to parse rendered file {config_file}:\n{err}\n\nfailed content written to {tmp_dump}')

        data, ok = validate_config(loaded)

        if not ok:
            tmp_dump = tmp.write_tmp(loaded, '.yml')
            return cli.abort(f'invalid config {config_file}:\n{format_errors(data)}\n\ndata dump written to {tmp_dump}')

        parsed.append(Config(conf_path, data))

    return parsed
