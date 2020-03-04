from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.validation import Validator
from prompt_toolkit.completion import WordCompleter


bool_completer = WordCompleter(['yes', 'no'])


def _validate_bool(text):
    return text.lower() in ('y', 'n', 'yes', 'no')


bool_validator = Validator.from_callable(
    _validate_bool,
    error_message='Enter one of yes/no (y/n)',
    move_cursor_to_end=True
)


def prompt_bool(message, session=None, default='no'):
    # type: (str, PromptSession, str) -> bool
    if session:
        pt = session.prompt
    else:
        pt = prompt

    res = pt(message,
             default=default,
             completer=bool_completer,
             validator=bool_validator)

    if session:
        session.validator = None
        session.completer = None

    return res in ('y', 'yes')
