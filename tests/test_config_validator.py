import yaml
from os.path import join, dirname
import unittest
import pytest

from kraken.common.app_config.schema import validate_config, print_errors

valid_config = {
    'version': '1.0',
    'environment': 'test',
    'kind': {
        'Namespace': {
            'part': 'test',
            'project_name': 'test',
            'global_env': 'test'
        }
    }
}

with open(join(dirname(__file__), 'data/conf/2-complex-v1.yml'), 'r') as f:
    complex_config = yaml.load(f, Loader=yaml.SafeLoader)

with open(join(dirname(__file__), 'data/conf/1-invalid-v1.yml'), 'r') as f:
    invalid_config = yaml.load(f, Loader=yaml.SafeLoader)


class ValidateTestCase(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    def test_validate_simple(self):
        data, ok = validate_config(valid_config)

        self.assertTrue(ok, data)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['version'], '1.0')

    def test_validate_complex(self):
        data, ok = validate_config(complex_config)

        self.assertTrue(ok, data)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['kind']['Deployment']['resources']['limits']['cpu'], '1')

    def test_validate_invalid_without_version(self):
        data, ok = validate_config(invalid_config)

        self.assertFalse(ok)
        self.assertIsInstance(data, dict)
        self.assertIn('required field', data['version'][0])

    def test_validate_invalid_with_version(self):
        invc = invalid_config.copy()
        invc['version'] = '1.0'
        data, ok = validate_config(invc)

        self.assertFalse(ok)
        self.assertIsInstance(data, dict)
        self.assertIn('Secret', data['kind'][0])
        self.assertIn('replicas', data['kind'][0]['Deployment'][0])

    def test_print_errors(self):
        invc = invalid_config.copy()
        invc['version'] = '1.0'
        data, ok = validate_config(invc)

        self.assertFalse(ok)

        print_errors(data)

        captured = self.capfd.readouterr()
        expected = '''Validation errors:
kind.Deployment.replicas:
  - min value is 0

kind.Secret:
  - must be of list type

'''
        self.assertEqual(captured.out, expected)

    def test_print_errors_header(self):
        invc = invalid_config.copy()
        invc['version'] = '1.0'
        data, ok = validate_config(invc)

        self.assertFalse(ok)

        print_errors(data, 'Error validating 1-invalid-v1.yaml:')

        captured = self.capfd.readouterr()
        expected = '''Error validating 1-invalid-v1.yaml:
kind.Deployment.replicas:
  - min value is 0

kind.Secret:
  - must be of list type

'''
        self.assertEqual(captured.out, expected)


if __name__ == '__main__':
    unittest.main()
