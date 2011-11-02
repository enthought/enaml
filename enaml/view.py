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

    def __getitem__(self, key):
        return getattr(self, key)


class View(object):
    """ The View object provides a simple shell around an Enaml ui tree.

    """
    def __init__(self, components, ns):
        self.components = components
        self.ns = NamespaceProxy(ns)
        if len(components) > 0:
            self.root = components[0]
        else:
            self.root = None

    def show(self, start_app=True):
        if len(self.components) > 1:
            msg = 'A View is currently unable to show multiple components'
            raise ValueError(msg)
        elif self.root is None:
            msg = 'A View must be given 1 component. Got 0.'
            raise ValueError(msg)

        component = self.root

        if not isinstance(component, Window):
            msg = 'A View is currently unable to show non-Window types'
            raise TypeError(msg)

        tk = component.toolkit
        tk.app = tk.create_app()

        component.show()

        if start_app:
            tk.start_app()

