#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
# Copyright (c) 2011 by Enthought, Inc.
# All rights reserved.

from setuptools import setup, find_packages

setup(name='enaml',
    version='0.1a',
    author='Enthought, Inc',
    author_email='info@enthought.com',
    url='https://github.com/enthought/enaml',
    description='Reactive language for building dynamic user interfaces with in Python',
    long_description=open('README.rst').read(),
    requires=['traits', 'PySide', 'ply', 'wx', 'argparse'],
    install_requires=['distribute'],
    package_data = {
        'enaml.stdlib': ['*.enaml']
    },
    packages=find_packages(),
    entry_points = dict(
        console_scripts = [
            "enaml-run = enaml.runner:main",
        ],
    ),
    test_suite = "enaml.test_collector"
)
