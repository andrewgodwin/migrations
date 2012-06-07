#!/usr/bin/env python

import os

# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

from south import __version__


# Build packages list
packages = []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('south2'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append(dirpath.strip("/").replace("/", "."))

setup(
    name='South',
    version=__version__,
    description='South: Migrations for Django',
    long_description='South is an intelligent database migrations library for the Django web framework. It is database-independent and DVCS-friendly, as well as a whole host of other features.',
    author='Andrew Godwin',
    author_email='south@aeracode.org',
    url='http://south.aeracode.org/',
    download_url='http://south.aeracode.org/wiki/Download',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    packages = packages,
)
