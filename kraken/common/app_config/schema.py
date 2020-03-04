from .schemas import load_schemas, set_condition
from collections import defaultdict

_schemas = None


def validate_config(cnf):
    # type: (dict) -> (dict, bool)
    """ Validates app deployment configuration against specific version.

    Returns tuple with (config, True) if configuration is valid (errors, False) otherwise.

    :param cnf: Configuration dict
    :return:
    """
    global _schemas
    if not _schemas:
        _schemas = load_schemas()

    doc = _schemas['default'].validated(cnf)
    if not doc:
        return _schemas['default'].errors, False

    valid_doc = _schemas[doc['version']].validated(doc)
    if not valid_doc:
        return _schemas[doc['version']].errors, False

    return valid_doc, True


def __unwrap_error_dict(errors, path=None):
    # type: (dict, str) -> dict
    res = defaultdict(list)
    for k, v in errors.items():
        kpath = f'{path}.{k}' if path else k

        for item in v:
            if type(item) is dict:
                res.update(__unwrap_error_dict(item, kpath))
            else:
                res[kpath].append(item)

    return res


def format_errors(errors):
    # type: (dict) -> str
    """ Format errors returned by validate_config in human readable format

    :param errors:
    :return:
    """
    out = []

    for k, v in __unwrap_error_dict(errors).items():
        out.append(f'{k}:')
        for err in v:
            out.append(f'  - {err}')
        out.append('')

    return '\n'.join(out)
