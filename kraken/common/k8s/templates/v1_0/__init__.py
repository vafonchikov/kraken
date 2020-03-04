import yaml
from typing import Dict
from os.path import join, dirname, isfile
from kraken.common.templating import render
from kraken.common.app_config.config import Config
from kraken.utils import cli, tmp

_tpl_root = dirname(__file__)


def render_config_templates(config, kind_filter=None):
    # type: (Config, list) -> Dict[str, dict]
    res = {}

    # template helper to read config files from app folder
    def _read_conf(filename):
        with open(join(config.directory, 'conf', filename), 'r') as cf:
            return cf.read()

    for name, data in config.kind.items():
        if kind_filter and not any(x.lower() in name.lower() for x in kind_filter):
            continue

        k8s_template = join(_tpl_root, f'{name}.yml')

        if not isfile(k8s_template):
            tmp_dump = tmp.write_tmp(config.data, '.yml')
            return cli.abort(f'missing k8s template for kind:{name}\nsource written to {tmp_dump}')

        with open(k8s_template, 'r') as f:
            try:
                rendered = render(f.read(), config.data, _tpl_root, {'conf': _read_conf})
            except Exception as err:
                tmp_dump = tmp.write_tmp(config.data, '.yml')
                return cli.abort(
                    f'failed to render k8s template for kind:{name}: {err}\nsource written to {tmp_dump}')

        try:
            loaded = yaml.load(rendered, Loader=yaml.SafeLoader)
        except Exception as err:
            tmp_dump = tmp.write_tmp(rendered, '.yml')
            return cli.abort(f'failed to load k8s template for kind:{name}: {err}\nsource written to {tmp_dump}')

        res[f'{config.name}-{name}.yml'] = loaded

    return res
