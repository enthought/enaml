# -*- coding: utf-8 -*-# Copyright (c) 2011 by Enthought, Inc.
# All rights reserved.

from setuptools import setup, find_packages

setup(name='traitsml',
    version='0.1a',
    author='Enthought, Inc',
    author_email='info@enthought.com',
    url='https://github.com/enthought/traitsml',
    description='language for building user interfaces with Traits',
    long_description=open('README.rst').read(),
    requires=['traits', 'PySide', 'ply', 'wx'],
    install_requires=['distribute'],
    packages=find_packages(),
    test_suite = "traitsml.test_collector"
)
