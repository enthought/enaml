#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode

from enaml.async.async_application import AsyncApplication
from .widget_component import WidgetComponent, SizeTuple


class Window(WidgetComponent):
    """ A top-level Window component.

    A Window component is represents of a top-level visible component
    with a frame decoration. It may have at most one child widget which
    is expanded to fit the size of the window. It does not support
    features like MenuBars or DockPanes, for that, use a MainWindow.

    """
    #: The titlebar text.
    title = Unicode

    #: The initial size of the window. A value of (-1, -1) indicates
    #: to let the client choose the initial size
    initial_size = SizeTuple

    #: The titlebar icon.
    # XXX needs to be implemented
    #icon = Instance()

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Return the attr initialization dict for a window.

        """
        super_attrs = super(Window, self).creation_attributes()
        attrs = {'title': self.title, 'initial_size': self.initial_size}
        super_attrs.update(attrs)
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Window, self).bind()
        self.publish_attributes('title')

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def close(self):
        """ Send a 'close' command to the client UI

        """
        self.send_message({'action': 'close'})

    def maximize(self):
        """ Send a 'maximize' command to the client UI.

        """
        self.send_message({'action': 'maximize'})

    def minimize(self):
        """ Send a 'minimize' command to the client UI.

        """
        self.send_message({'action': 'minimize'})

    def restore(self):
        """ Send a 'restore' command to the client UI.

        """
        self.send_message({'action': 'restore'})

    def publish(self):
        """ Publish this Window with the application. 

        This method takes care of ensuring that all the child widgets
        are also published and that all of the binding/initialization
        handlers are called.
        
        """
        # XXX We are currently assuming all children will be messenger 
        # widgets. This will probably need to be updated at some
        # point in the future. Use cases will be the deciders.
        widgets = []
        stack = [self]
        while stack:
            widget = stack.pop()
            widgets.append(widget)
            stack.extend(widget.children)

        targets = []
        for widget in widgets:
            targets.append(widget.target_id)
        
        app = AsyncApplication.instance()
        app.publish(targets)
        
        for widget in widgets:
            widget.bind()

