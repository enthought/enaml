#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os
from setuptools import setup, find_packages, Extension, Feature


enaml_extensions = Feature(
    description='optional optimized c++ extensions',
    standard=bool(os.environ.get('BUILD_ENAML_EXTENSIONS')),
    ext_modules=[
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
        )
    ],
)


setup(
    name='enaml',
    version='0.6.8',
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
    test_suite='enaml.test_collector',
    features={'enaml-extensions': enaml_extensions}
)

