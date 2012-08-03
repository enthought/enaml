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


class SimpleSession(Session):
    """ A concrete Session class that receives a callable, positional,
    and keyword arguments and creates the associated view(s).
    
    """
    def init(self, sess_callable, *args, **kwargs):
        """ Initialize the session with the callable and arguments.
        
        """
        self.sess_callable = sess_callable
        self.args = args
        self.kwargs = kwargs
    
    def on_open(self):
        """ Create the view from the callable
        
        """
        views = self.sess_callable(*self.args, **self.kwargs)
        if not isinstance(views, Iterable):
            views = [views]
        return views


def simple_session(sess_name, sess_descr, sess_callable, *args, **kwargs):
    """ Creates a SessionFactory instance for a callable.
    
    This creates a SessionFactory instance which will create instances
    of SimpleSession when prompted by the application.
    
    Parameters
    ----------
    sess_name : str
        A unique, human-friendly name for the session.
    
    sess_descr : str
        A brief description of the session.

    sess_callable : callable
        A callable which will return an Enaml view or iterable of views.

    *args, **kwargs
        Optional positional and keyword arguments to pass to the callable
        when the session is created.

    """
    fact = SessionFactory(
        sess_name, sess_descr, SimpleSession, sess_callable, *args, **kwargs
    )
    return fact


def view_factory(sess_name=None, sess_descr=None):
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
            return simple_session(_name, _descr, func, *args, **kwargs)
        return closure
    if sess_name is not None and callable(sess_name):
        return wrapper(sess_name, None, sess_descr)
    def _wrapper(func):
        return wrapper(func, sess_name, sess_descr)
    return _wrapper


def simple_app(sess_name, sess_descr, sess_callable, *args, **kwargs):
    """ Utility function which creates an application from a component.
    
    This is suitable for use in simple applications, particularly 
    "traditional" GUI applications running a single main view in a 
    single process.
    
    Parameters
    ----------
    sess_name : str
        An unique, human-friendly name for the session.
    
    sess_descr : str
        An brief description of the session.
    
    sess_callable : callable
        A callable which returns a component or iterable of components
        for the session.

    *args, **kwargs
        Optional positional and keyword arguments to pass to the 
        callable when the session is opened.
    
    """
    from enaml.application import Application
    factory = simple_session(
        sess_name, sess_descr, sess_callable, *args, **kwargs
    )
    app = Application([factory])
    return app

