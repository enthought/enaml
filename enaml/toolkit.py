#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import Sequence
import os

from traits.api import HasStrictTraits, Callable

from .expressions import (DefaultExpression, BindingExpression, 
                          DelegateExpression, NotifierExpression)


class Constructor(HasStrictTraits):
    """ The constructor class to use to populate the toolkit.

    Attributes
    ----------
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
        component = component_cls(toolkit_impl=impl_cls())
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
        stack = cls.__stack__
        if not stack:
            tk = cls.default_toolkit()
        else:
            tk = stack[-1]
        return tk 

    @classmethod
    def default_toolkit(cls):
        tk = cls.__default__
        if tk is None:
            tk = cls.__default__ = default_toolkit()
        return tk

    def __enter__(self):
        self.__stack__.append(self)
    
    def __exit__(self, *args, **kwargs):
        self.__stack__.pop()

    def _get_default(self):
        return self['__enaml_default__']
    
    def _set_default(self, val):
        self['__enaml_default__'] = val
    
    default = property(_get_default, _set_default)

    def _get_bind(self):
        return self['__enaml_bind__']
    
    def _set_bind(self, val):
        self['__enaml_bind__'] = val
    
    bind = property(_get_bind, _set_bind)

    def _get_delegate(self):
        return self['__enaml_delegate__']
    
    def _set_delegate(self, val):
        self['__enaml_delegate__'] = val
    
    delegate = property(_get_delegate, _set_delegate)

    def _get_notify(self):
        return self['__enaml_notify__']
    
    def _set_notify(self, val):
        self['__enaml_notify__'] = val
    
    notify = property(_get_notify, _set_notify)

    def _get_style_sheet(self):
        return self['__style_sheet__']
    
    def _set_style_sheet(self, val):
        self['__style_sheet__'] = val

    style_sheet = property(_get_style_sheet, _set_style_sheet)

    def _get_create_app(self):
        return self['__create_app__']
    
    def _set_create_app(self, val):
        self['__create_app__'] = val
    
    create_app = property(_get_create_app, _set_create_app)

    def _get_start_app(self):
        return self['__start_app__']
    
    def _set_start_app(self, val):
        self['__start_app__'] = val

    start_app = property(_get_start_app, _set_start_app)

    def _get_app(self):
        return self['__app__']
    
    def _set_app(self, val):
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
    # from .util.guisupport import get_app_wx, start_event_loop_wx
    # #from .widgets.wx import constructors as ctors
    # from .widgets.wx import dialogs
    # from .widgets.wx.styling import WX_STYLE_SHEET

    # utils = {
    #     'error': dialogs.error,
    #     'warning': dialogs.warning,
    #     'information': dialogs.information,
    #     'question': dialogs.question
    # }

    # ctors = None

    # toolkit = Toolkit(get_app_wx, start_event_loop_wx, constructors=ctors, 
    #                   utils=utils, style_sheet=WX_STYLE_SHEET)

    return # toolkit


def qt_toolkit():
    """ Creates and return a toolkit object for the Qt backend.

    """
    from .widgets.qt.constructors import QT_CONSTRUCTORS
    from .util.guisupport import get_app_qt4, start_event_loop_qt4
    from .widgets.qt.styling import QT_STYLE_SHEET

    utils = {}

    toolkit = Toolkit(QT_CONSTRUCTORS)
    
    toolkit.create_app = get_app_qt4
    toolkit.start_app = start_event_loop_qt4
    toolkit.style_sheet = QT_STYLE_SHEET
    toolkit.default = DefaultExpression
    toolkit.bind = BindingExpression
    toolkit.delegate = DelegateExpression
    toolkit.notify = NotifierExpression
    toolkit.update(utils)

    return toolkit 

