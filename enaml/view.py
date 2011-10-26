#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .widgets.window import Window

  
class NamespaceProxy(object):
    """ A simple proxy object that converts a namespace dictionary
    into an object with attribute-like access.

    """
    def __init__(self, ns):
        self.__dict__ = ns
      

class View(object):
    """ The View object provides a simple shell around an Enaml ui tree.

    """
    def __init__(self, components, ns):
        self.components = components
        self.ns = NamespaceProxy(ns)

    def show(self, start_app=True):
        components = self.components
        
        if len(components) > 1:
            msg = 'A View is currently unable to show multiple components'
            raise ValueError(msg)
        
        component = components[0]
        
        if not isinstance(component, Window):
            msg = 'A View is currently unable to show non-Window types'
            raise TypeError(msg)
        
        tk = component.toolkit
        tk.create_app()
        
        component.show()
        
        if start_app:
            tk.start_app()

