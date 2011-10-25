#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import Sequence
import os

from traits.api import HasStrictTraits, Callable, Str


class Constructor(HasStrictTraits):
    """ The constructor class to use to populate the toolkit.

    Attributes
    ----------
    type_name : Str
        The name of the type, as seen from enaml source code, that this
        constructor is creating. This is assigned by the toolkit object.

    component_loader : Callable
        A callable object which returns the component class to use
        for the widget.
    
    impl_loader : Callable
        A callable object which returns the implementation class to 
        use for the widget.
    
    Methods
    -------
    build(*arg, **kwargs)
        Calls the loaders and assembles the component.
    
    clone(component_loader=None, impl_loader=None)
        Creates a clone of this constructor, optionally changing
        out one of the loaders.
    
    """
    type_name = Str

    component_loader = Callable

    impl_loader = Callable

    def __init__(self, component_loader, impl_loader):
        """ Initialize a constructor instance.

        Parameters
        ----------
        component_loader : Callable
            A callable object which returns the component class to use
            for the widget.
    
        impl_loader : Callable
            A callable object which returns the implementation class to 
            use for the widget.
        
        """
        super(Constructor, self).__init__()
        self.component_loader = component_loader
        self.impl_loader = impl_loader

    def __call__(self, *args, **kwargs):
        """ Called by the vm to create the component(s) for this widget.
        This should not typically be overridden by sublasses. To perform
        specialized building behavior, override the `build` method.

        """
        result = self.build(*args, **kwargs)
        if not isinstance(result, Sequence):
            raise TypeError('Constructor results must be a sequence')
        return result

    def build(self, *args, **kwargs):
        """ Calls the loaders and assembles the component.

        Subclasses should override this method to implement custom 
        construction behavior if the default is not sufficient.

        Parameters
        ----------
        *args, **kwargs
            The args and kwargs with which this constructor was called 
            from the enaml source code.

        """
        component_cls = self.component_loader()
        impl_cls = self.impl_loader()
        component = component_cls(abstract_widget=impl_cls())
        return (component,)
    
    def clone(self, component_loader=None, impl_loader=None):
        """ Creates a clone of this constructor, optionally changing
        out one or both of the loaders.

        """
        if component_loader is None:
            component_loader = self.component_loader
        if impl_loader is None:
            impl_loader = self.impl_loader
        return Constructor(component_loader, impl_loader)


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

    def __init__(self, *args, **kwargs):
        """ Initialize a toolkit object using the same constructor 
        signature as dict(). This overridden constructor ensure that 
        type names are properly assigned to to constructors.

        """
        super(Toolkit, self).__init__(*args, **kwargs)
        for key, value in self.iteritems():
            if isinstance(value, Constructor):
                value.type_name = key
    
    def __setitem__(self, key, value):
        """ Overridden dict.__setitem__ to apply type name values to 
        constructors.

        """
        if isinstance(value, Constructor):
            value.type_name = key
        super(Toolkit, self).__setitem__(key, value)

    def update(self, other=None, **kwargs):
        """ Overridden from dict.update to apply type name values to 
        constructors.

        """
        if other is None:
           pass
        elif hasattr(other, 'iteritems'):
            for k, v in other.iteritems():
                self[k] = v
        elif hasattr(other, 'keys'):
            for k in other.keys():
                self[k] = other[k]
        else:
            for k, v in other:
                self[k] = v
        if kwargs:
            self.update(kwargs)
    
    def setdefault(self, key, default=None):
        """ Overridden from dict.setdefault to apply type name values to 
        constructors.
        
        """ 
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default

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

    def _get_style_sheet(self):
        """ Returns the default style sheet instance for this toolkit.

        """
        return self['__style_sheet__']
    
    def _set_style_sheet(self, val):
        """ Sets the default style sheet instance for this toolkit.

        """
        self['__style_sheet__'] = val

    style_sheet = property(_get_style_sheet, _set_style_sheet)

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
        return self['__app__']
    
    def _set_app(self, val):
        """ Sets the application object for this toolkit.

        """
        self['__app__'] = val
    
    app = property(_get_app, _set_app)


def default_toolkit():
    """ Creates an returns the default toolkit object based on
    the user's current ETS_TOOLKIT environment variables.

    """
    toolkit = os.environ.get('ETS_TOOLKIT', 'wx').lower()
    
    if toolkit == 'wx':
        return wx_toolkit()
        
    if toolkit == 'qt' or toolkit == 'qt4':
        return qt_toolkit()
    
    raise ValueError('Invalid Toolkit: %s' % toolkit)


def wx_toolkit():
    """ Creates and return a toolkit object for the Wx backend.

    """
    from .widgets.wx.constructors import WX_CONSTRUCTORS
    from .util.guisupport import get_app_wx, start_event_loop_wx
    from .widgets.wx.styling import WX_STYLE_SHEET

    utils = {}

    toolkit = Toolkit(WX_CONSTRUCTORS)
    
    toolkit.create_app = get_app_wx
    toolkit.start_app = start_event_loop_wx
    toolkit.style_sheet = WX_STYLE_SHEET
    toolkit.update(utils)

    return toolkit


def qt_toolkit():
    """ Creates and return a toolkit object for the Qt backend.

    """
    from .operators import OPERATORS
    from .widgets.qt.constructors import QT_CONSTRUCTORS
    from .util.guisupport import get_app_qt4, start_event_loop_qt4
    from .widgets.qt.styling import QT_STYLE_SHEET

    utils = {}

    toolkit = Toolkit(QT_CONSTRUCTORS)
    
    toolkit.create_app = get_app_qt4
    toolkit.start_app = start_event_loop_qt4
    toolkit.style_sheet = QT_STYLE_SHEET
    toolkit.update(utils)
    toolkit.update(OPERATORS)

    return toolkit 

