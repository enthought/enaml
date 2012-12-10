#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os
from setuptools import setup, find_packages, Extension


if os.environ.get('BUILD_ENAML_EXTENSIONS'):
    ext_modules = [
        Extension(
            'enaml.extensions.weakmethod',
            ['enaml/extensions/weakmethod.cpp'],
            language='c++',
        ),
        Extension(
            'enaml.extensions.callableref',
            ['enaml/extensions/callableref.cpp'],
            language='c++',
        ),
        Extension(
           'enaml.extensions.signaling',
           ['enaml/extensions/signaling.cpp'],
           language='c++',
        ),
        Extension(
            'enaml.extensions.funchelper',
            ['enaml/extensions/funchelper.cpp'],
            language='c++',
        ),
    ]
else:
    ext_modules = []


setup(
    name='enaml',
    version='0.6.1',
    author='Enthought, Inc',
    author_email='info@enthought.com',
    url='https://github.com/enthought/enaml',
    description='Declarative language for building dynamic user interfaces '
                'in Python',
    long_description=open('README.rst').read(),
    requires=['traits', 'PySide', 'ply', 'wx', 'casuarius'],
    install_requires=['distribute'],
    packages=find_packages(),
    package_data={'enaml.stdlib': ['*.enaml']},
    entry_points = dict(
        console_scripts=[
            'enaml-run = enaml.runner:main',
        ],
    ),
    ext_modules=ext_modules,
    test_suite='enaml.test_collector',
)

