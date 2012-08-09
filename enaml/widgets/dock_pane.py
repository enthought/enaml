#------------------------------------------------------------------------------
# Copyright (c) 2012, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Enum, Unicode, Bool,  Property, cached_property

from enaml.core.trait_types import EnamlEvent

from .container import Container
from .widget_component import WidgetComponent


class DockPane(WidgetComponent):
    """ A widget which can be docked in a MainWindow.

    A DockPane is a widget which can be docked in designated dock areas
    in a MainWindow. I can have at most a single child widget which is 
    an instance of Container.

    """
    #: The title of the dock pane.
    title = Unicode

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
    #: docked manually via the 'dock_area' attribute.
    allowed_dock_areas = List(
        Enum('left', 'right', 'top', 'bottom', 'all'), value=['all'],
    )

    #: A read only property which returns the dock widget for the pane.
    dock_widget = Property(depends_on='children[]')

    #: An event fired when the user closes the page by clicking on 
    #: the tab's close button. This event is fired by the parent 
    #: MainWindow when the tab is closed. This event has no payload.
    closed = EnamlEvent

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the DockPane.

        """
        snap = super(DockPane, self).snapshot()
        snap['dock_widget_id'] = self._snap_dock_widget_id()
        snap['title'] = self.title
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
            'title', 'title_bar_orientation', 'closable', 'movable',
            'floatable', 'floating', 'dock_area', 'allowed_dock_areas'
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
            The dock widget for the Pane, or None if not provided.

        """
        for child in self.children:
            if isinstance(child, Container):
                return child

    def _snap_dock_widget_id(self):
        """ Returns the widget id for the dock widget or None.

        """
        dock_widget = self.dock_widget
        if dock_widget is not None:
            return dock_widget.widget_id

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_floating_changed(self, content):
        """ Handle the 'floating_changed' action from the client 
        widget.

        """
        self.set_guarded(floating=content['floating'])

    def on_action_dock_area_changed(self, content):
        """ Handle the 'dock_area_changed' action from the client 
        widget.

        """
        self.set_guarded(dock_area=content['dock_area'])
    
    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self):
        """ A convenience method for calling 'open_dock_pane' on the
        parent MainWindow, passing this pane as an argument.

        """
        parent = self.parent
        if parent is not None:
            parent.open_dock_pane(self)

    def close(self):
        """ A convenience method for calling 'close_dock_pane' on the
        parent MainWindow, passing this page as an argument.

        """ 
        parent = self.parent
        if parent is not None:
            parent.close_dock_pane(self)

