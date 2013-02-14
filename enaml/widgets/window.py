#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Enum, Property, Str, Bool, cached_property

from enaml.core.trait_types import EnamlEvent

from .container import Container
from .widget import Widget, SizeTuple


class Window(Widget):
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

    #: An enum which indicates the modality of the window. The default
    #: value is 'non_modal'.
    modality = Enum('non_modal', 'application_modal', 'window_modal')

    #: Whether or not the window remains on top of all others.
    always_on_top = Bool(False)

    #: If this value is set to True, the window will be destroyed on
    #: the completion of the `closed` event.
    destroy_on_close = Bool(True)

    #: An event fired when the window is closed.
    closed = EnamlEvent

    #: Returns the central widget in use for the Window
    central_widget = Property(depends_on='children')

    #: The source url for the titlebar icon.
    icon_source = Str

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for a Window.

        """
        snap = super(Window, self).snapshot()
        snap['title'] = self.title
        snap['initial_size'] = self.initial_size
        snap['modality'] = self.modality
        snap['always_on_top'] = self.always_on_top
        snap['icon_source'] = self.icon_source
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Window, self).bind()
        attrs = ('title', 'modality', 'always_on_top', 'icon_source')
        self.publish_attributes(*attrs)

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
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_closed(self, content):
        """ Handle the 'closed' action from the client widget.

        """
        self.set_guarded(visible=False)
        self.closed()
        if self.destroy_on_close:
            self.destroy()

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

    def send_to_front(self):
        """ Send the 'send_to_front' action to the client widget.

        This moves the window to the front of all the toplevel windows.

        """
        self.send_action('send_to_front', {})

    def send_to_back(self):
        """ Send the 'send_to_back' action to the client widget.

        This moves the window to the back of all the toplevel windows.

        """
        self.send_action('send_to_back', {})

