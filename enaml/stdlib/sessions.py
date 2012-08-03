#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Enaml Standard Library - Sessions

This module contains some Session subclasses and associated utilities that
handle common Session cases.

"""

from ..session import Session

class _ComponentSession(Session):
    """ Abstract Session that expects an Enaml component and creates a view
    
    To use this, create a subclass with a class attribute or method "component".
    
    """

    #: the component object used by the class
    component = None
    
    def initialize(self, *args, **kwargs):
        """ Initialize the session with the arguments for the component
        
        """
        self.args = args
        self.kwargs = kwargs
    
    def on_open(self):
        """ Create the view from the component
        
        """
        view = self.component(*self.args, **self.kwargs)
        return view


def ComponentSession(component, name=None, description=None):
    """ Class factory that creates a Session class for an Enaml component
    
    This creates a Session class that creates an instance of the specified
    component when the on_open() method is called.
    
    Parameters
    ----------
    component : Enaml component
        The component to wrap into a session

    name : string
        An optional unique, human-friendly name.
    
    description : string
        An optional brief description of the session.
    
    """
    session_class = type('ComponentHandlerSession', (_ComponentSession,),
        {'component': component})
    if name is not None:
        session_class.name = name
    if description is not None:
        session_class.description = description
    return session_class


def _view_handler(name, description):
    """ Utility decorator that pre-fills session name and description

    Parameters
    ----------
    name : string
        An optional unique, human-friendly name.
    
    description : string
        An optional brief description of the session.
   
    """
    def decorator(component):
        Session = ComponentSession(component, name, description)
        handler_factory = Session.create_handler
        return handler_factory
        

def view_handler(*args, **kwargs):
    """ Decorator that creates a handler factory for a view factory.
    
    This can be used either as::
        
        @view_handler
        def view(...):
            ...
            return [View1(...), View2(...)]
    
    or for a component::
    
        handler = view_handler(Main)
    
    or::
    
        @view_handler('my-view', 'This is my view')
        def view(...):
            ...
            return [View1(...), View2(...)]
    
    """
    if len(args) == 1 and callable(args[0]):
        component = args[0]
        Session = ComponentSession(component)
        handler_factory = Session.create_handler
        return handler_factory
    else:
        return _view_handler(*args, **kwargs)


def single_view_app(component, session_name, session_description, *args,
        **kwargs):
    """ Utility function which creates an application from a component
    
    This is suitable for use in simple applications, particularly "traditional"
    GUI applications running a single main view in a single process.
    
    Parameters
    ----------
    component : Enaml component
        The component to wrap into a session

    name : string
        An optional unique, human-friendly name.
    
    description : string
        An optional brief description of the session.
    
    args : tuple
        Optional positional arguments to be passed to the component by the
        Session when opened.
        
    kwargs : dict
        Optional keyword arguments to be passed to the component by the
        Session when opened.
    
    """
    from ..application import Application
    handler = view_handler(component)
    app = Application([handler(session_name, session_description, *args,
        **kwargs)])
    return app
    
