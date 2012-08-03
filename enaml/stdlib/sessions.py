#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Enaml Standard Library - Sessions

This module contains some Session subclasses and associated utilities that
handle common Session cases.

"""
from collections import Iterable
from functools import wraps

from enaml.session import Session
from enaml.session_factory import SessionFactory


class ComponentSession(Session):
    """ A concrete Session class that receives a callable, positional,
    and keyword arguments and creates the associated view(s).
    
    """
    def init(self, component, *args, **kwargs):
        """ Initialize the session with the arguments for the component
        
        """
        self.component = component
        self.args = args
        self.kwargs = kwargs
    
    def on_open(self):
        """ Create the view from the component.
        
        """
        comp = self.component(*self.args, **self.kwargs)
        if not isinstance(comp, Iterable):
            comp = [comp]
        return comp


def component_session(name, description, component, *args, **kwargs):
    """ Creates a SessionFactory instance for a callable.
    
    This creates a SessionFactory instance which will create instances
    of ComponentSession when prompted by the application.
    
    Parameters
    ----------
    name : str
        A unique, human-friendly name.
    
    description : str
        A brief description of the session.

    component : callable
        A callable which will return an Enaml view or iterable of views.

    *args, **kwargs
        Optional positional and keyword arguments to pass to the callable
        when the session is created.

    """
    fact = SessionFactory(
        name, description, ComponentSession, component, *args, **kwargs
    )
    return fact


def view_factory(name=None, description=None):
    """ A decorator that creates a session factory from a function.
     
    This can be used in the following ways:
        
        @view_factory
        def view(...):
            ...
            return View(...)
        
        @view_factory('my-views', 'This is several view')
        def views(...):
            ...
            return [View1(...), View2(...)]
    
        simple = view_factory(Main)
    
    """
    def wrapper(func, _name, _descr):
        if _name is None:
            _name = func.__name__
        if _descr is None:
            _descr = func.__doc__ or 'no description'
        @wraps(func)
        def closure(*args, **kwargs):
            return component_session(_name, _descr, func, *args, **kwargs)
        return closure
    if name is not None and callable(name):
        return wrapper(name, None, description)
    def _wrapper(func):
        return wrapper(func, name, description)
    return _wrapper


def single_view_app(name, description, component, *args, **kwargs):
    """ Utility function which creates an application from a component.
    
    This is suitable for use in simple applications, particularly 
    "traditional" GUI applications running a single main view in a 
    single process.
    
    Parameters
    ----------
    name : str
        An ounique, human-friendly name.
    
    description : str
        An brief description of the session.
    
    component : callable
        A callable which returns a component or iterable of components.

    *args, **kwargs
        Optional positional and keyword arguments to pass to the 
        callable when the session is opened.
    
    """
    from enaml.application import Application
    factory = component_session(name, description, component, *args, **kwargs)
    app = Application([factory])
    return app

