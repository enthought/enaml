#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Property, cached_property

from enaml.core.trait_types import EnamlEvent

from .container import Container
from .widget_component import WidgetComponent, SizeTuple


class Window(WidgetComponent):
    """ A top-level Window component.

    A Window component is represents of a top-level visible component
    with a frame decoration. It may have at most one child widget which
    is dubbed the 'central widget'. The central widget is an instance
    of Container and is expanded to fit the size of the window.

    A Window does not support features like MenuBars or DockPanes, for 
    such functionality, use a MainWindow widget.

    """
    #: The titlebar text.
    title = Unicode

    #: The initial size of the window. A value of (-1, -1) indicates
    #: to let the client choose the initial size
    initial_size = SizeTuple

    #: An event fired when the window is closed.
    closed = EnamlEvent

    #: Returns the central widget in use for the Window
    central_widget = Property(depends_on='children[]')

    #: The titlebar icon.
    # XXX needs to be implemented
    #icon = Instance()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_central_widget(self):
        """ The getter for the 'central_widget' property.

        Returns
        -------
        result : Container or None
            The central widget for the Window, or None if not provieded.

        """
        for child in self.children:
            if isinstance(child, Container):
                return child

    def _snap_central_widget(self):
        """ Returns the widget id of the central widget or None.

        """
        widget = self.central_widget
        if widget is not None:
            return widget.widget_id

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for a Window.

        """
        snap = super(Window, self).snapshot()
        snap['title'] = self.title
        snap['initial_size'] = self.initial_size
        snap['central_widget'] = self._snap_central_widget()
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Window, self).bind()
        self.publish_attributes('title')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_closed(self, content):
        """ Handle the 'closed' action from the client widget.

        """
        self.closed()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def close(self):
        """ Send the 'close' action to the client widget.

        """
        self.send_action('close', {})

    def maximize(self):
        """ Send the 'maximize' action to the client widget.

        """
        self.send_action('maximize', {})

    def minimize(self):
        """ Send the 'minimize' action to the client widget.

        """
        self.send_action('minimize', {})

    def restore(self):
        """ Send the 'restore' action to the client widget.

        """
        self.send_action('restore', {})

