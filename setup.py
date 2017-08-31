#!/usr/bin/env python3

import setuptools
import sys

setuptools.setup(
    name='prefer',
    setup_requires=[
        'PyYAML',
        'xmljson',
    ],
    tests_require=[
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'pytest-runner',
        'pytest-watch',
    ],
)
