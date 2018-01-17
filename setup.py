#!/usr/bin/env python3

import setuptools
import sys

setup_requires = []

if {'pytest', 'test', 'ptr'}.intersection(sys.argv):
    setup_requires.append('pytest-runner')

setuptools.setup(setup_requires=setup_requires)
