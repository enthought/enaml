# Copyright (c) 2011 by Enthought, Inc.
# All rights reserved.

from distutils.core import setup


setup(name = 'traitsml',
    version='0.1a',
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    url = 'https://github.com/enthought/traitsml',
    description = 'language for building user interfaces with Traits',
    long_description = open('README.rst').read(),
    requires = ['traits', 'PySide', 'ply'],
    packages = [
        'traitsml',
        'traitsml.parsing',
        'traitsml.pyside',
        'traitsml.view_elements',
    ],
)
