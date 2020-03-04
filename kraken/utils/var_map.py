import yaml
import os


class VariableMap(object):
    """ Convenience helper to store key-value mapping
    """
    def __init__(self, **kwargs):
        self.__dict = {}
        self.__dict.update(kwargs)

    def read_yaml(self, filename):
        """ Read values from .yaml file

        :param filename:
        :return:
        """
        with open(filename, 'r') as f:
            self.__dict.update(yaml.load(f, Loader=yaml.SafeLoader))

    def read_env(self, ignored_keys=None):
        """ Read values from environment

        :param ignored_keys: list of keys that should not be added to map
        :return:
        """
        if not ignored_keys:
            ignored_keys = []

        if type(ignored_keys) not in (list, dict):
            raise TypeError("ignored_keys must be list or tuple")

        self.__dict.update(dict((k, v) for k, v in os.environ.items() if k not in ignored_keys))

    def set(self, key, value):
        """ Set single key-value pair

        :param key:
        :param value:
        """
        self.__dict[key] = value

    def get(self, key, default=None):
        """ Retrieve stored value by ``key``.
        If no variable with ``key`` is set then return ``default``
        :param key:
        :param default:
        :return:
        """
        return self.__dict[key] if key in self.__dict else default

    def update(self, dct: dict):
        """ Update stored values from other dict

        :param dct:
        """
        self.__dict.update(dct)

    def dict(self):
        """ Return all stored values as dictionary

        :return:
        """
        return self.__dict
