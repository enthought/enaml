#------------------------------------------------------------------------------
# Copyright (c) 2012, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    List, Enum, Unicode, Bool, Instance, Property, cached_property,
)

from enaml.core.trait_types import EnamlEvent

from .container import Container
from .widget_component import WidgetComponent


class DockPane(WidgetComponent):
    """ A DockPane is a widget which holds a single child Container
    and can be docked in arbitrary locations in a MainWindow.

    """
    #: The title of the dock pane.
    title = Unicode

    #: Whether or not the dock area is closable via a close button.
    closable = Bool(True)

    #: Whether or not the dock area is movable from its current position.
    movable = Bool(True)

    #: Whether or not the dock are is floatable as a separate window.
    floatable = Bool(True)
    
    #: A boolean indicating whether or not the dock pane is floating.
    floating = Bool(False)

    #: The orientation of the title bar.
    title_bar_orientation = Enum('horizontal', 'vertical')

    #: The dock area in which the pane currently resides.
    dock_area = Enum('left', 'right', 'top', 'bottom')

    #: The areas in the main window in which this dock area is allowed
    #: to be docked via user interaction.
    allowed_dock_areas = List(
        Enum('left', 'right', 'top', 'bottom', 'all'), value=['all'],
    )

    #: A read only property which returns the dock widget for the pane.
    dock_widget = Property(depends_on='children[]')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_dock_widget(self):
        """ The getter for the 'dock_widget' property.

        Returns
        -------
        result : Container or None
            The dock widget for the Pane, or None if no dock widget
            is provided.

        """
        for child in self.children:
            if isinstance(child, Container):
                return child

    def _snap_dock_widget(self):
        """ Returns the serializable target ids for the dock widget.

        """
        dock_widget = self.dock_widget
        if dock_widget is not None:
            return dock_widget.widget_id

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the DockPane.

        """
        snap = super(DockPane, self).snapshot()
        snap['dock_widget'] = self._snap_dock_widget()
        return snap

