#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" An amalgamation of utilities used throughout the Enaml framework.

"""
class abstractclassmethod(classmethod):
    """ A backport of the Python 3's abc.abstractclassmethod.

    """
    __isabstractmethod__ = True

    def __init__(self, func):
        func.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(func)

