#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os


#------------------------------------------------------------------------------
# Toolkit
#------------------------------------------------------------------------------
class Toolkit(dict):
    """ The Enaml toolkit object class which facilitates easy gui
    toolkit independent backend development and use. The Toolkit
    is a dict subclass which is injected between the module and
    builtin scopes when executing an Enaml function or expression.

    XXX - more documentation

    """
    __stack__ = []

    __default__ = None

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
        tk = cls.__default__
        if tk is None:
            tk = cls.__default__ = default_toolkit()
        return tk

    def __enter__(self):
        """ A context manager method that pushes this toolkit onto
        the active toolkit stack.

        """
        self.__stack__.append(self)

    def __exit__(self, *args, **kwargs):
        """ A context manager method that pops this toolkit from the
        active toolkit stack.

        """
        self.__stack__.pop()

    def _get_create_app(self):
        """ Returns the app creation function for this toolkit.

        """
        return self['__create_app__']

    def _set_create_app(self, val):
        """ Sets the app creation function for this toolkit.

        """
        self['__create_app__'] = val

    create_app = property(_get_create_app, _set_create_app)

    def _get_start_app(self):
        """ Returns the start app function for this toolkit.

        """
        return self['__start_app__']

    def _set_start_app(self, val):
        """ Sets the start app function for this toolkit.

        """
        self['__start_app__'] = val

    start_app = property(_get_start_app, _set_start_app)

    def _get_app(self):
        """ Returns the application object for this toolkit.

        """
        return self.get('__app__')

    def _set_app(self, val):
        """ Sets the application object for this toolkit.

        """
        self['__app__'] = val

    app = property(_get_app, _set_app)

    def _get_process_events(self):
        return self['__process_events__']
    
    def _set_process_events(self, val):
        self['__process_events__'] = val

    process_events = property(_get_process_events, _set_process_events)

    def _get_invoke_later(self):
        """ Returns the function for invoking a function later in the event
        loop.

        """
        return self.get('__invoke_later__')

    def _set_invoke_later(self, val):
        self['__invoke_later__'] = val

    invoke_later = property(_get_invoke_later, _set_invoke_later)

    def _get_invoke_timer(self):
        """ Returns the function for invoking a function some ms later in
        the event loop.

        """
        return self.get('__invoke_timer__')

    def _set_invoke_timer(self, val):
        self['__invoke_timer__'] = val

    invoke_timer = property(_get_invoke_timer, _set_invoke_timer)

    def _get_control_exception_handler(self):
        """ Returns the function for handling exceptions on a control object
        that would otherwise be swallowed.
        
        """
        return self['__control_exception_handler__']
    
    def _set_control_exception_handler(self, val):
        self['__control_exception_handler__'] = val
        
    control_exception_handler = property(_get_control_exception_handler, 
                                         _set_control_exception_handler)


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
    from .widgets.qt.constructors import QT_CONSTRUCTORS
    from .util.guisupport import get_app_qt4, start_event_loop_qt4, process_events_qt4
    from .widgets.qt.utils import invoke_later, invoke_timer
    from .widgets.layout.layout_helpers import LAYOUT_HELPERS
    from .widgets.constructors import CONSTRUCTORS

    utils = {}

    toolkit = Toolkit(QT_CONSTRUCTORS)
    toolkit.update(CONSTRUCTORS)

    toolkit.create_app = get_app_qt4
    toolkit.start_app = start_event_loop_qt4
    toolkit.process_events = process_events_qt4
    toolkit.invoke_later = invoke_later
    toolkit.invoke_timer = invoke_timer
    toolkit.control_exception_handler = None
    toolkit.update(utils)
    toolkit.update(OPERATORS)
    toolkit.update(LAYOUT_HELPERS)

    return toolkit


def wx_toolkit():
    """ Creates and return a toolkit object for the Wx backend.

    """
    from .operators import OPERATORS
    from .widgets.wx.constructors import WX_CONSTRUCTORS
    from .util.guisupport import get_app_wx, start_event_loop_wx, process_events_wx
    from .widgets.wx.utils import invoke_later, invoke_timer
    from .widgets.layout.layout_helpers import LAYOUT_HELPERS
    from .widgets.constructors import CONSTRUCTORS

    utils = {}

    toolkit = Toolkit(WX_CONSTRUCTORS)
    toolkit.update(CONSTRUCTORS)
    
    toolkit.create_app = get_app_wx
    toolkit.start_app = start_event_loop_wx
    toolkit.process_events = process_events_wx
    toolkit.invoke_later = invoke_later
    toolkit.invoke_timer = invoke_timer
    toolkit.control_exception_handler = None
    toolkit.update(utils)
    toolkit.update(OPERATORS)
    toolkit.update(LAYOUT_HELPERS)

    return toolkit

