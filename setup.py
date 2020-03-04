import os
import re
import codecs
from setuptools import setup, find_packages


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = [
    'Click >= 7.0, < 8',
    'Cerberus >= 1.3, < 2',
    'PyYAML >= 5.1, < 6',
    'kubernetes >= 10.0.1, < 11',
    'jinja2 >= 2.10, < 3',
    'docker >= 4.1.0, < 5',
    'prompt_toolkit >= 2.0, < 3'
]

test_requires = [
    'pytest >= 5.2, < 6'
]

setup(
    name='kraken',
    version=find_version('kraken', '__init__.py'),
    description='Tool for deploying projects to k8s cluster',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    url='https://git.vsemayki.pro/etc/kraken',
    author='vsemayki.devops',
    license='MIT',
    project_urls={
        'Source': 'https://git.vsemayki.pro/etc/kraken',
        'Tracker': 'https://git.vsemayki.pro/etc/kraken/issues'
    },
    install_requires=install_requires,
    test_requires=test_requires,
    python_requires='>=3.3',
    entry_points={'console_scripts': 'kraken=kraken:run_cli'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
