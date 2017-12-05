#!/usr/bin/env python

import os
from setuptools import setup, find_packages
#from onevizion import __version__
__version__ = '1.0.0'

#following PyPI guide: https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(name='onevizion',
    version = __version__,
    author="OneVizion",
    author_email="development@onevizion.com",
    url="https://github.com/Onevizion/API-v3",
    classifiers=[
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Unix",
    "Programming Language :: Python",
    ],
    packages = find_packages(),

    platforms=["Unix"],
    license="MIT",
    description="onevizion wraps the version 3 API for a OneVizion system, and provides a few optional other utilities.",
    long_description=read('README.md'),
)
