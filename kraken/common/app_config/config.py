import re
from os.path import basename, splitext, dirname

_filename_re = re.compile(r"(\d+)-(.*)\.ya?ml", re.IGNORECASE)


class Config(object):
    """ Object that holds single processed application config

    """
    def __init__(self, filename, data):
        self.__filename = filename
        self.__data = data

    @property
    def filename(self):
        # type: () -> str
        return basename(self.__filename)

    @property
    def directory(self):
        # type: () -> str
        return dirname(self.__filename)

    @property
    def name(self):
        # type: () -> str
        name, _ = splitext(basename(self.__filename))
        return name

    @property
    def order(self):
        # type: () -> str
        matches = _filename_re.match(basename(self.__filename))
        return matches.group(1) if matches else None

    @property
    def piece_name(self):
        # type: () -> str
        matches = _filename_re.match(basename(self.__filename))
        return matches.group(2) if matches else None

    @property
    def data(self):
        # type: () -> dict
        return self.__data

    @property
    def version(self):
        # type: () -> str
        return self.__data['version']

    def __getattr__(self, item):
        return self.__data[item]

    def __str__(self):
        return f"Config(filename='{self.__filename}', data={self.__data})"

    def __repr__(self):
        return str(self)
