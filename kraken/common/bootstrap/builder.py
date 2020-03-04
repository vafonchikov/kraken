from os.path import isdir, isfile, join, dirname, isabs
from os import mkdir
from shutil import copyfile
from prompt_toolkit import print_formatted_text, HTML
from kraken.common.templating import render


_template_dir = join(dirname(__file__), 'templates')


class BuilderBase:
    __template_file__ = None

    def __init__(self):
        self._answers = []

        self._should_make_values_yaml = False
        self._should_make_env_file = False
        self._copy_configs = []

    def run(self, base_dir='.k8s'):
        """ Main builder method
        Call it to ask for input and write configuration files

        :param base_dir:
        :return:
        """
        if not self.__template_file__:
            raise RuntimeError('child builders must specify __template_file__ property')

        print_formatted_text(HTML('''<ansigreen>Welcome to new project configuration master!
You will be asked several questions during process to properly setup basic files.</ansigreen>
'''))

        self.make_answers()
        self.validate_and_write_files(base_dir)

    def make_answers(self):
        raise NotImplementedError()

    def validate_and_write_files(self, base_dir):
        with open(join(_template_dir, self.__template_file__), 'r') as f:
            template_content = f.read()

        create_dirs = [base_dir, join(base_dir, 'conf'), join(base_dir, 'docker')]

        for _dir in create_dirs:
            if not isdir(_dir):
                mkdir(_dir)

        for conf in self._copy_configs:
            src = conf['src']
            dst = join(base_dir, conf['dst'])

            if not isabs(src):
                src = join(_template_dir, src)

            if not isfile(dst):
                copyfile(src, dst)
            else:
                print_formatted_text(HTML(
                    f'<ansired>warn: copy of {conf["src"]}->{conf["dst"]} failed: '
                    'destination file already exists</ansired>'
                ))

        env_file = join(base_dir, '_envs.yml')
        values_file = join(base_dir, 'values.yml')

        if self._should_make_values_yaml and not isfile(values_file):
            with open(values_file, 'w+') as f:
                f.write('# Put extra values here\n# VAR_NAME: VAR_VALUE\n\n')

        if self._should_make_env_file and not isfile(env_file):
            with open(env_file, 'w+') as f:
                f.write('# Put env in format\n#- name: VAR_NAME\n#  value: VAR_VALUE\n\n')

        for idx, desc in enumerate(self._answers):
            conf_file_name = f'{idx+1}-{desc["part_name"]}.yml'
            conf_file = join(base_dir, conf_file_name)

            if isfile(conf_file):
                raise RuntimeError(f'cannot create {conf_file_name}: file already exists')

            with open(conf_file, 'w+') as f:
                f.write(render(template_content, desc, base_dir=_template_dir))

        print_formatted_text(HTML(f'''
<ansigreen>Configuration files written to {base_dir}!</ansigreen>
'''))


class UnsupportedVersion(Exception):
    pass


_builder_versions = {}


def register_builder(ver):
    def _wrapper(cls):
        _builder_versions[ver] = cls
        return cls

    return _wrapper


def create_builder(version='v1'):
    # type: (str) -> BuilderBase
    if version in _builder_versions:
        return _builder_versions[version]()

    raise UnsupportedVersion(version)
