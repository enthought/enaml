#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os


#------------------------------------------------------------------------------
# Toolkit
#------------------------------------------------------------------------------
class Toolkit(dict):
    """ The Enaml Toolkit class which facilitates toolkit independent
    development. 

    The Toolkit is a dict subclass which is injected between the global 
    and builtin scopes of an executing an Enaml function or expression.
    The contents of the dictionary may consist of any useful objects
    that should be automatically in scope for executing Enaml code. 
    Typical content of a toolkit will include component constructors, 
    layout helpers, operators, and useful toolkit abstractions.

    """
    __stack__ = []

    __default_toolkit__ = None

    __toolkit_app__ = None

    @classmethod
    def active_toolkit(cls):
        """ A classmethod that returns the currently active toolkit,
        or the default toolkit if there is not active toolkit context.

        """
        stack = cls.__stack__
        if not stack:
            tk = cls.default_toolkit()
        else:
            tk = stack[-1]
        return tk

    @classmethod
    def default_toolkit(cls):
        """ A classmethod that returns the default toolkit, creating one
        if necessary.

        """
        tk = cls.__default_toolkit__
        if tk is None:
            tk = cls.__default_toolkit__ = default_toolkit()
        return tk

    def __enter__(self):
        """ A context manager method that pushes this toolkit onto
        the active toolkit stack.

        """
        self.__stack__.append(self)

    def __exit__(self, exc_type, exc_value, traceback):
        """ A context manager method that pops this toolkit from the
        active toolkit stack.

        """
        self.__stack__.pop()

    def _get_toolkit_app(self):
        """ Returns the abstract toolkit app for this toolkit or
        raises an ValueError if one is not defined.

        """
        return self.__toolkit_app__

    def _set_toolkit_app(self, val):
        """ Sets the abstract toolkit app for this toolkit and makes
        it available in the toolkit's namespace under the 'toolkit_app'
        name.

        """
        self.__toolkit_app__ = val

    app = property(_get_toolkit_app, _set_toolkit_app)


#------------------------------------------------------------------------------
# Toolkit Factory Functions
#------------------------------------------------------------------------------
def default_toolkit():
    """ Creates an returns the default toolkit object based on
    the user's current ETS_TOOLKIT environment variables.

    """
    toolkit = os.environ.get('ETS_TOOLKIT', 'qt').lower()

    if toolkit == 'qt' or toolkit == 'qt4':
        return qt_toolkit()

    if toolkit == 'wx':
        return wx_toolkit()

    raise ValueError('Invalid Toolkit: %s' % toolkit)


def qt_toolkit():
    """ Creates and return a toolkit object for the Qt backend.

    """
    from .operators import OPERATORS
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
    from .operators import OPERATORS
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

