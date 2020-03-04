from importlib import import_module
from typing import Dict
from os.path import join, dirname, isdir
from kraken.common.app_config.config import Config
from kraken.utils import cli


def render_from_config(config, kind_filter=None):
    # type: (Config, list) -> Dict[str, dict]
    """ Render k8s templates from app config

    :param config:
    :param kind_filter:
    :return:
    """
    root_dir = dirname(__file__)
    module_name = "v" + config.version.replace('.', '_')

    if isdir(join(root_dir, module_name)):
        m = import_module(__name__ + "." + module_name)
        return m.render_config_templates(config, kind_filter)

    cli.abort(f'unsupported config version {config.version}')
