from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator
from kraken.utils.prompt import prompt_bool
from os.path import isfile
from .builder import BuilderBase, register_builder

_kind_types = ['Deployment', 'CronJob', 'Job', 'Ingress', 'Service']
kind_completer = WordCompleter(_kind_types)

path_validator = Validator.from_callable(
    lambda text: isfile(text),
    error_message='invalid path: file does not exist',
    move_cursor_to_end=True
)


@register_builder('v1')
class _BuilderV1(BuilderBase):
    __template_file__ = 'config_v1.tpl.yml'

    def make_answers(self):
        session = PromptSession()

        while True:
            answers = {
                'part_name': session.prompt('Enter part name: ').strip()
            }

            while True:
                kind_type = session.prompt('What type of service you want to create? ',
                                           completer=kind_completer).strip()

                if kind_type not in _kind_types:
                    print_formatted_text(HTML(f'<ansired>Invalid type. Choose one from '
                                              f'{", ".join(_kind_types)}</ansired>'))
                break

            answers[f'has_{kind_type.lower()}'] = True

            if answers.get('has_deployment', False):
                self._ask_deployment(session, answers)
            if answers.get('has_cronjob', False):
                self._ask_cronjob(session, answers)
            if answers.get('has_job', False):
                self._ask_job(session, answers)
            if answers.get('has_service', False):
                self._ask_service(session, answers)
            if answers.get('has_ingress', False):
                self._ask_ingress(session, answers)

            self._answers.append(answers)

            if not prompt_bool('Do you want to create another config? ', session):
                break

        if not self._should_make_env_file:
            self._should_make_env_file = prompt_bool('Create global _envs.yml file? ', session)

        if not self._should_make_values_yaml:
            self._should_make_values_yaml = prompt_bool('Create values.yml file for extra variables? ', session)

        for ans in self._answers:
            if 'has_secret' in ans:
                self._copy_configs.append({
                    'src': 'conf/dockerconfigjson',
                    'dst': 'conf/dockerconfigjson'
                })
                break

    def _ask_deployment(self, session, answers):
        answers['containers'] = []

        if prompt_bool('Would this deployment have ingress? ', session):
            answers['has_ingress'] = True
            answers['has_service'] = True

        if not answers.get('has_service', False) and prompt_bool('Would this deployment have service?', session):
            answers['has_service'] = True

        while True:
            container = {}
            self._ask_container(session, container, answers)

            answers['containers'].append(container)

            if not prompt_bool('Create another container? ', session):
                return

    def _ask_job(self, session, answers):
        answers['containers'] = []

        while True:
            container = {}
            self._ask_container(session, container, answers)

            answers['containers'].append(container)

            if not prompt_bool('Create another container? ', session):
                return

    def _ask_cronjob(self, session, answers):
        sched = session.prompt('Enter cronjob schedule: ', default='0 * * * *')

        answers['schedule'] = sched
        answers['containers'] = []

        while True:
            container = {}
            self._ask_container(session, container, answers)

            answers['containers'].append(container)

            if not prompt_bool('Create another container? ', session):
                return

    def _ask_container(self, session, answers, global_answers):
        answers['name'] = session.prompt('Enter container name: ')

        if prompt_bool('Will container use global _envs.yml file? ', session):
            answers['use_env_file'] = True
            if not self._should_make_env_file:
                self.__should_make_env_file = True

        if prompt_bool('Will container have external port? ', session):
            answers['port'] = session.prompt('Enter container port: ')

            if prompt_bool('Create service for this port? ', session):
                global_answers['has_service'] = True
                global_answers['service_app_port'] = answers['port']
                global_answers['service_port'] = answers['port']

        if prompt_bool('Do you have dockerfile for this container? ', session):
            path = session.prompt('Enter path to dockerfile: ', validator=path_validator)

            self._copy_configs.append({
                'src': path,
                'dst': f'docker/Dockerfile-{global_answers["part_name"]}'
            })

            global_answers['has_secret'] = True

        elif prompt_bool('Will this container use existing image from hub.docker.com? ', session):
            img = session.prompt('Enter image to use: ')

            parts = img.split(':')
            if len(parts) == 1:
                dimg = parts[0]
                dtag = session.prompt('Enter image tag: ', default='latest')
            else:
                dimg = parts[0]
                dtag = parts[1]

            answers['docker_img'] = dimg
            answers['build_tag'] = dtag
        else:
            print_formatted_text(HTML('<ansiblue>Empty dockerfile will be created with part name</ansiblue>'))
            self._copy_configs.append({
                'src': 'conf/Dockerfile',
                'dst': f'docker/Dockerfile-{global_answers["part_name"]}'
            })
            global_answers['has_secret'] = True

    def _ask_service(self, session, answers):
        if not answers.get('service_app_port') and prompt_bool('Customize service ports? (default 80) ', session):
            answers['service_port'] = session.prompt('Enter service port: ', default='80')
            answers['service_app_port'] = session.prompt('Enter service app_port: ', default='80')

    def _ask_ingress(self, session, answers):
        if prompt_bool('Is this ingress for specific service? ', session):
            answers['ingress_service'] = {
                'name': session.prompt('Enter service name: '),
                'port': session.prompt('Enter service port: ')
            }

        if prompt_bool('Customize application url? ', session):
            answers['ingress_url'] = session.prompt('Enter application url: ')
