import yaml
from os import listdir
from os.path import join, dirname, basename, splitext
from cerberus import Validator, schema_registry, rules_set_registry

_conditions = {}


def set_condition(name, value):
    global _conditions
    _conditions[name] = value


class OptionalValidator(Validator):
    priority_validations = ('maybe_nullable', 'nullable', 'readonly', 'type', 'empty')

    def _validate_maybe_nullable(self, condition, field, value):
        """Conditionally apply nullable rule

        The rule's arguments are validated against this schema:
        {'type': 'dict', 'keysrules': {'type': 'string'}}
        """
        if value is None:
            for k, v in condition.items():
                if _conditions.get(k, None) != v:
                    return

            self._drop_remaining_rules(
                'allowed',
                'empty',
                'forbidden',
                'items',
                'keysrules',
                'min',
                'max',
                'minlength',
                'maxlength',
                'regex',
                'schema',
                'type',
                'valuesrules',
                'nullable',
            )


def load_schemas():
    # type: () -> dict
    """ Parse all schemas defined in current directory and return it as a map of validators

    :return:
    """
    root = dirname(__file__)
    files = [f for f in listdir(root) if f.endswith('.yaml')]

    versions = 'versions.yaml'

    if versions not in files:
        raise RuntimeError('missing required config versions.yaml')

    files.remove(versions)
    # sort versions in asc order
    files = list(sorted(files))

    for file in files:
        with open(join(root, file)) as f:
            conf = yaml.load(f, Loader=yaml.SafeLoader)

        conf_name, _ = splitext(basename(file))

        for schema_name, desc in conf.get('schemas', {}).items():
            schema_registry.add(f'{conf_name}.{schema_name}', desc)

        for rule_name, desc in conf.get('rules', {}).items():
            rules_set_registry.add(f'{conf_name}.{rule_name}', desc)

    with open(join(root, versions)) as f:
        wconf = yaml.load(f, Loader=yaml.SafeLoader)

    if '_all' not in wconf:
        raise RuntimeError('invalid versions.yaml: missing _all section')

    if 'versions' not in wconf:
        raise RuntimeError('invalid versions.yaml: missing versions section')

    res = {
        'default': OptionalValidator(wconf['_all'], allow_unknown=True)
    }

    for ver, desc in wconf['versions'].items():
        desc.update(wconf['_all'])
        res[str(ver)] = OptionalValidator(desc)

    return res
