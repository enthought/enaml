#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasStrictTraits, Instance, Bool

from .toolkit import Toolkit
from .style_sheet import StyleSheet
from .widgets.component import Component
from .widgets.window import Window

  
class NamespaceProxy(object):
    """ A simple proxy object that converts a namespace dictionary
    into an object with attribute-like access.

    """
    def __init__(self, ns):
        self.__dict__ = ns
      

class View(HasStrictTraits):
    """ The View object provides a simple shell around an Enaml ui tree.

    Attributes
    ----------
    window : Instance(Window)
        The top-level Enaml window object for the view.

    ns : Instance(NamespaceProxy)
        A proxy into the global namespace of the enaml view.

    toolkit : Instance(Toolkit)
        The toolkit instance that was used to create the view.
    
    Methods
    -------
    show()
        Show the ui on the screen.

    hide()
        Hide the ui from the screen.

    """
    component = Instance(Component)

    ns = Instance(NamespaceProxy)

    toolkit = Instance(Toolkit)

    def show(self, start_loop=True):
        component = self.component
        if not isinstance(component, Window):
            raise TypeError('Can only show Windows.')
        self.toolkit.create_app()
        component.show()
        if start_loop:
            self.toolkit.start_loop()
        
    def apply_style_sheet(self):
        stack = [self.component]
        style_sheet = self.toolkit.style_sheet
        while stack:
            component = stack.pop()
            component.set_style_sheet(style_sheet)
            stack.extend(component.children)

