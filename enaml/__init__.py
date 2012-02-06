#-----------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os
import sys


#------------------------------------------------------------------------------
# Import Helper
#------------------------------------------------------------------------------
def imports():
    """ Lazily imports and returns an enaml imports context.

    """
    from .core.import_hooks import imports
    return imports()


#------------------------------------------------------------------------------
# Toolkit Factory Functions
#------------------------------------------------------------------------------
#: The private storage for the optional default toolkit function which 
#: overrides that which is computed from environment variables.
_default_toolkit_func = None


def set_default_toolkit_func(func):
    """ Set the default toolkit function to the given callable.

    Parameters
    ----------
    func : callable
        A callable object which takes no arguments and returns an
        instance of Toolkit.
    
    """
    global _default_toolkit_func
    _default_toolkit_func = func


def reset_default_toolkit_func():
    """ Reset the default toolkit func such that the default toolkit
    is computed from environment variables.

    """
    global _default_toolkit_func
    _default_toolkit_func = None


def default_toolkit():
    """ Creates an returns the default toolkit object based on the user's
    current ETS_TOOLKIT environment variables, or the default toolkit
    function supplied via the set_default_toolkit_func function.

    """
    tk_func = _default_toolkit_func
    if tk_func is not None:
        return tk_func()

    toolkit = os.environ.get('ETS_TOOLKIT', 'qt').lower()

    if toolkit == 'qt' or toolkit == 'qt4':
        return qt_toolkit()

    if toolkit == 'wx':
        return wx_toolkit()

    raise ValueError('Invalid Toolkit: %s' % toolkit)


def qt_toolkit():
    """ Creates and return a toolkit object for the Qt backend.

    """
    from .core.operators import OPERATORS
    from .core.toolkit import Toolkit
    from .widgets.constructors import CONSTRUCTORS
    from .widgets.layout.layout_helpers import LAYOUT_HELPERS
    from .widgets.qt.constructors import QT_CONSTRUCTORS
    from .widgets.qt.qt_application import QtApplication

    toolkit = Toolkit(QT_CONSTRUCTORS)
    toolkit.update(CONSTRUCTORS)
    toolkit.update(OPERATORS)
    toolkit.update(LAYOUT_HELPERS)
    toolkit.app = QtApplication()

    return toolkit


def wx_toolkit():
    """ Creates and return a toolkit object for the Wx backend.

    """
    from .core.operators import OPERATORS
    from .core.toolkit import Toolkit
    from .widgets.constructors import CONSTRUCTORS
    from .widgets.layout.layout_helpers import LAYOUT_HELPERS
    from .widgets.wx.constructors import WX_CONSTRUCTORS
    from .widgets.wx.wx_application import WXApplication

    toolkit = Toolkit(WX_CONSTRUCTORS)
    toolkit.update(CONSTRUCTORS)
    toolkit.update(OPERATORS)
    toolkit.update(LAYOUT_HELPERS)
    toolkit.app = WXApplication()

    return toolkit


#------------------------------------------------------------------------------
# Test Helpers
#------------------------------------------------------------------------------
def test_collector():
    """ Discover and collect tests for the Enaml Package.

        .. note :: addapted from the unittest2
    """
    from unittest import TestLoader

    # import __main__ triggers code re-execution
    __main__ = sys.modules['__main__']
    setupDir = os.path.abspath(os.path.dirname(__main__.__file__))

    return TestLoader().discover(setupDir)

