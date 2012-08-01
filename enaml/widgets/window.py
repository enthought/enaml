#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode

from enaml.core.trait_types import EnamlEvent

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

    #: An event fired when the window is closed.
    closed = EnamlEvent

    #: The titlebar icon.
    # XXX needs to be implemented
    #icon = Instance()

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for a Window.

        """
        snap = super(Window, self).snapshot()
        snap['title'] = self.title
        snap['initial_size'] = self.initial_size
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

