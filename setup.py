# Copyright (c) 2012 by Enthought, Inc.
# All rights reserved.

from setuptools import setup, find_packages

kwds = {}

try:
    from distutils.core import Extension
    from Cython.Distutils import build_ext

    # only build the speedups Cython C extension when Cython is installed
    kwds['cmdclass'] = {'build_ext': build_ext}
    kwds['ext_modules'] = [Extension('enaml.speedups.model_index',
                                     ['enaml/speedups/model_index.pyx'])]
except ImportError:
    pass


setup(
    name='enaml',
    version='0.1',
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
        console_scripts = [
            "enaml-run = enaml.runner:main",
        ],
    ),
    test_suite = "enaml.test_collector",
    **kwds
)
