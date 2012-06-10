#!/usr/bin/env python

import os

# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

from migrations import __version__

# Build packages list
packages = []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('migrations'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append(dirpath.strip("/").replace("/", "."))

setup(
    name = 'django.contrib.migrations',
    version = __version__,
    description = 'Django Migrations',
    long_description = "Django's migration framework",
    author = 'Andrew Godwin',
    author_email = 'south@aeracode.org',
    packages = packages,
)
