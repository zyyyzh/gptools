#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

setup(
    author="Zihao Ye, Alexander Maertens",
    description="gptools",
    name='gptools',
    packages=find_packages(include=['gptools']),
    package_data={'': []},
    include_package_data=True,
    version='0.0.3',
)
