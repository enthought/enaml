#------------------------------------------------------------------------------
# Copyright (c) 2012, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Enum, Unicode, Bool,  Property, cached_property

from enaml.core.trait_types import EnamlEvent

from .container import Container
from .widget import Widget


class DockPane(Widget):
    """ A widget which can be docked in a MainWindow.

    A DockPane is a widget which can be docked in designated dock areas
    in a MainWindow. It can have at most a single child widget which is
    an instance of Container.

    """
    #: The title to use in the title bar.
    title = Unicode

    #: Whether or not the title bar is visible.
    title_bar_visible = Bool(True)

    #: The orientation of the title bar.
    title_bar_orientation = Enum('horizontal', 'vertical')

    #: Whether or not the dock pane is closable via a close button.
    closable = Bool(True)

    #: Whether or not the dock pane is movable by the user.
    movable = Bool(True)

    #: Whether or not the dock can be floated as a separate window.
    floatable = Bool(True)

    #: A boolean indicating whether or not the dock pane is floating.
    floating = Bool(False)

    #: The dock area in the MainWindow where the pane is docked.
    dock_area = Enum('left', 'right', 'top', 'bottom')

    #: The dock areas in the MainWindow where the pane can be docked
    #: by the user. Note that this does not preclude the pane from
    #: being docked programmatically via the 'dock_area' attribute.
    allowed_dock_areas = List(
        Enum('left', 'right', 'top', 'bottom', 'all'), value=['all'],
    )

    #: A read only property which returns the pane's dock widget.
    dock_widget = Property(depends_on='children')

    #: An event fired when the user closes the pane by clicking on the
    #: dock pane's close button.
    closed = EnamlEvent

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the DockPane.

        """
        snap = super(DockPane, self).snapshot()
        snap['title'] = self.title
        snap['title_bar_visible'] = self.title_bar_visible
        snap['title_bar_orientation'] = self.title_bar_orientation
        snap['closable'] = self.closable
        snap['movable'] = self.movable
        snap['floatable'] = self.floatable
        snap['floating'] = self.floating
        snap['dock_area'] = self.dock_area
        snap['allowed_dock_areas'] = self.allowed_dock_areas
        return snap

    def bind(self):
        super(DockPane, self).bind()
        attrs = (
            'title', 'title_bar_visible', 'title_bar_orientation', 'closable',
            'movable', 'floatable', 'floating', 'dock_area',
            'allowed_dock_areas'
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_dock_widget(self):
        """ The getter for the 'dock_widget' property.

        Returns
        -------
        result : Container or None
            The dock widget for the DockPane, or None if not provided.

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

    def on_action_floated(self, content):
        """ Handle the 'floated' action from the client widget.

        """
        self.set_guarded(floating=True)

    def on_action_docked(self, content):
        """ Handle the 'docked' action from the client widget.

        """
        self.set_guarded(floating=False)
        self.set_guarded(dock_area=content['dock_area'])

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self):
        """ Open the dock pane in the MainWindow.

        Calling this method will also set the pane visibility to True.

        """
        self.set_guarded(visible=True)
        self.send_action('open', {})

    def close(self):
        """ Close the dock pane in the MainWindow.

        Calling this method will set the pane visibility to False.

        """
        self.set_guarded(visible=False)
        self.send_action('close', {})

