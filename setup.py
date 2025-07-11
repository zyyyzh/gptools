#!/usr/bin/env python

"""
The setup script.
Date:2025-07-11
"""

from setuptools import setup, find_packages

setup(
    author="Zihao Ye, Alexander Maertens",
    description="gptools",
    name='gptools',
    packages=find_packages(include=['gptools']),
    package_data={'': []},
    include_package_data=True,
    version='0.0.5',
)
