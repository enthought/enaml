#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import functools


DEPRECATED_FUNCTION = ('The %s function is deprecated and will be removed in '
                       'future versions of Enaml.')


def deprecated(func):
    """ A decorator which will raise a DeprecationWarning when the 
    wrapped function is executed.

    """
    @functools.wraps(func)
    def closure(*args, **kwargs):
        import warnings
        warnings.warn(DEPRECATED_FUNCTION % func.__name__, DeprecationWarning)
        return func(*args, **kwargs)
    return closure

