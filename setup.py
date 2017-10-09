#!/usr/bin/env python3

import setuptools
import sys

TEST_COMMANDS = {'pytest', 'test', 'ptr'}


def is_running_tests():
    return TEST_COMMANDS.intersection(sys.argv)


dependencies = [
    'PyYAML',
    'xmljson',
]

if is_running_tests:
    dependencies.append('pytest-runner')

setuptools.setup(
    name='prefer',
    setup_requires=dependencies,
    tests_require=[
        'mock',
        'mypy',
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'pytest-watch',
        'pytest-blockage',
    ],
)
