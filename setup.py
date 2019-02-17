#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0',
                'pokebase==1.2.0',
                'pyaml>=18.11.0',
                'fabulous>=0.3.0',
                'click_completion>=0.5.0',
                'psutil>=5.5.1']

setup_requirements = []

test_requirements = ['httpretty==0.9.6']

dev_requirements = ['bumpversion==0.5.3',
                    'watchdog==0.9.0',
                    'flake8==3.5.0',
                    'tox==3.5.2',
                    'coverage==4.5.1',
                    'Sphinx==1.8.1',
                    'twine==1.12.1']

setup(
    author="Matthew M Stratton",
    author_email='matthew.m.stratton@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    description="Application to help train competitive pokemon",
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pokemon_trainer',
    name='pokemon_trainer',
    url='https://github.com/macgregor/pokemon_trainer',
    version='0.1.0',
    zip_safe=False,
    packages=find_packages(include=['pokemon_trainer']),
    entry_points={
        'console_scripts': [
            'pokemon-trainer=pokemon_trainer.cli:main',
        ],
    },
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'test': test_requirements
    },
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    test_suite='tests'
)
