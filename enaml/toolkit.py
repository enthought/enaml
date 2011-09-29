#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os

from traits.api import HasStrictTraits, Dict, Str, Callable, Any, Instance

from .constructors import IToolkitConstructor, BaseToolkitCtor
from .style_sheet import StyleSheet
from .util.trait_types import SubClass
from .expressions import (
    IExpressionNotifierFactory, IExpressionDelegateFactory,
    DefaultExpressionFactory, BindingExpressionFactory,
    DelegateExpressionFactory, NotifierExpressionFactory,
)


def _derived_ctor(name, component_cls, ctor):
    """ A factory function which creates a derived constructor class.

    Parameters
    ----------
    name : string
        The type name of the derived ctor.

    component_cls : class
        The component class to use in the ctor.
    
    ctor : BaseToolkitCtor subclass
        The constructor class to use to get the impl class.
    
    Returns
    -------
    result : BaseToolkCtor subclass
        A new constructor class.
    
    """
    class DerivedCtor(BaseToolkitCtor):

        @classmethod
        def component_class(cls):
            return component_cls
        
        @classmethod
        def impl_class(cls):
            return ctor.impl_class()
        
        @classmethod
        def type_name(cls):
            return name
    
    return DerivedCtor


def _extract_ctors(mod):
    """ Yields valid ctors from a module. Used by the toolkit factory
    functions in this module.

    """
    for name in dir(mod):
        item = getattr(mod, name)
        if isinstance(item, type):
            if issubclass(item, BaseToolkitCtor):
                try:
                    item.type_name()
                except Exception:
                    pass
                else:
                    yield item


class Toolkit(HasStrictTraits):
    """ A simple class that handles toolkit related functionality.

    """
    _constructors = Dict(Str, SubClass(IToolkitConstructor))

    _create_toolkit_app = Callable

    _start_toolkit_loop = Callable

    _utils = Dict(Str, Callable)

    _style_sheet = Instance(StyleSheet)
    
    _default_expr = SubClass(IExpressionDelegateFactory)

    _bind_expr = SubClass(IExpressionDelegateFactory)

    _delegate_expr = SubClass(IExpressionDelegateFactory)

    _notify_expr = SubClass(IExpressionNotifierFactory)

    _toolkit_app = Any

    def __init__(self, create_app, start_loop, constructors=None, utils=None, 
                 style_sheet=None, default=None, bind=None, delegate=None, 
                 notify=None):
        super(Toolkit, self).__init__()
        self._create_toolkit_app = create_app
        self._start_toolkit_loop = start_loop
        self._utils = utils or {}
        self._style_sheet = style_sheet or StyleSheet()
        self._default_expr = default or DefaultExpressionFactory
        self._bind_expr = bind or BindingExpressionFactory
        self._delegate_expr = delegate or DelegateExpressionFactory
        self._notify_expr = notify or NotifierExpressionFactory

        if constructors is not None:
            for ctor in constructors:
                self.add_constructor(ctor)

    def create_app(self):
        """ Call this method to create the underlying toolkit specific 
        application object.

        """
        self._toolkit_app = self._create_toolkit_app()
    
    def start_loop(self):
        """ Call this method to start the toolkit specific event loop.
        This should typically be called only after 'create_app' has
        been called.

        """
        self._start_toolkit_loop(self._toolkit_app)

    def get_app(self):
        """ Call this method to retrieve the toolkit specific application
        object. This will return None until 'create_app' has been called.

        """
        return self._toolkit_app

    def add_constructor(self, ctor):
        """ Add/override a new constructor to the toolkit.

        Parameters
        ----------
        ctor : IToolkitConstructor subclass
            A class which will create instances that implement the
            IToolkitConstructor interface.
        
        """
        self._constructors[ctor.type_name()] = ctor

    def create_constructor(self, type_name, identifier):
        """ Instantiate a constructor for the given type_name.
        
        Creates and returns a constructor instance for the given type name
        using the provided identifier. If no constructor is registered with
        the given type name, then a ValueError will be raised.

        Parameters
        ----------
        type_name : string
            The type names of the widget from the enaml source code for 
            widget constructor that should be created.
        
        identifier : string
            The identifier of the widget being created in the enaml 
            source code.

        """
        try:
            ctor_cls = self._constructors[type_name]
        except KeyError:
            msg = 'Toolkit does not support the %s item.' % type_name
            raise ValueError(msg)
        return ctor_cls(identifier)

    def add_derived_component(self, component, type_name=None, ctor_name=None):
        """ Add a derived enaml component widget to the toolkit.

        Add a derived enaml component widget to the toolkit. This method
        will automatically determine an appropriate constructor to use.
        For example, if one has a simple subclass of an enaml Field,
        call this method with that subclass and a new constructor will
        be created for the subclass using the toolkit implementation 
        class for Field or another appropriate constructor. If no 
        appropriate constructor can be determined, a TypeError will be
        raise.

        Parameters
        ----------
        component : enaml.widgets.Component subclass
            The Component subclass to add to the toolkit.
        
        type_name : string, optional
            If provided, this is the name that will be used for the new
            component in the enaml source code. If omitted, the class name
            of the component will be used.
        
        ctor_name : string, optional
            If provided, the constructor for this name will be used as
            the constuctor from which to derived. Otherwise, the mro of
            the component class will be traversed to try to find a 
            suitable constructor. In that case, a match will be found
            if there is a constructor with a type_name that equals the
            name of a class in the mro *and* the new component class
            is a subclass of the component class in that constructor.

        """
        _constructors = self._constructors
        if ctor_name is not None:
            if ctor_name not in _constructors:
                raise ValueError('No constructor for `%s` name.' % ctor_name)
            ctor = _constructors[ctor_name]
        else:
            for cls in component.mro():
                name = cls.__name__
                if name in _constructors:
                    ctor = _constructors[name]
                    break
            else:
                msg = 'No suitable constructor could be found for `%s`.'
                raise TypeError(msg % component)

        if type_name is None:
            type_name = component.__name__

        derived = _derived_ctor(type_name, component, ctor)
        self.add_constructor(derived)

    def default(self, py_ast):
        """ Creates and returns an expression factory which uses default
        value binding semantics.

        Parameters
        ----------
        py_ast : ast.Expression
            A python Expression ast node.
        
        Returns
        -------
        result : IExpressionDelegate
            An object which implements the IExpressionDelegate interface.

        """
        return self._default_expr(py_ast)

    def bind(self, py_ast):
        """ Creates and returns an expression factory which uses 
        expression binding semantics.

        Parameters
        ----------
        py_ast : ast.Expression
            A python Expression ast node.
        
        Returns
        -------
        result : IExpressionDelegate
            An object which implements the IExpressionDelegate interface.

        """
        return self._bind_expr(py_ast)
    
    def delegate(self, py_ast):
        """ Creates and returns an expression factory which uses 
        delegation binding semantics.

        Parameters
        ----------
        py_ast : ast.Expression
            A python Expression ast node.
        
        Returns
        -------
        result : IExpressionDelegate
            An object which implements the IExpressionDelegate interface.
            
        """
        return self._delegate_expr(py_ast)
    
    def notify(self, py_ast):
        """ Creates and returns an expression factory which uses
        notification binding semantics.

        Parameters
        ----------
        py_ast : ast.Expression
            A python Expression ast node.
        
        Returns
        -------
        result : IExpressionDelegate
            An object which implements the IExpressionDelegate interface.
            
        """
        return self._notify_expr(py_ast)

    @property
    def style_sheet(self):
        return self._style_sheet
        

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
    """ Creates and return a toolkit object for the wx backend.

    """
    from .util.guisupport import get_app_wx, start_event_loop_wx
    from .widgets.wx import constructors
    from .widgets.wx import dialogs
    from .widgets.wx.styling import WX_STYLE_SHEET

    utils = {
        'error': dialogs.error,
        'warning': dialogs.warning,
        'information': dialogs.information,
        'question': dialogs.question
    }

    ctors = _extract_ctors(constructors)

    toolkit = Toolkit(get_app_wx, start_event_loop_wx, constructors=ctors, 
                      utils=utils, style_sheet=WX_STYLE_SHEET)

    return toolkit


def qt_toolkit():
    """ Creates and return a toolkit object for the PySide Qt backend.

    """
    from .util.guisupport import get_app_qt4, start_event_loop_qt4
    from .widgets.qt import constructors
    from .widgets.qt.styling import QT_STYLE_SHEET

    utils = {}

    ctors = _extract_ctors(constructors)

    toolkit = Toolkit(get_app_qt4, start_event_loop_qt4, constructors=ctors, 
                      utils=utils, style_sheet=QT_STYLE_SHEET)

    return toolkit 

