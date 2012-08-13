#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Enum, List

from .constraints_widget import ConstraintsWidget


class ToolBar(ConstraintsWidget):
    """ A tool bar widget.

    """
    #: Whether or not the tool bar is movable by the user.
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

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the DockPane.

        """
        snap = super(ToolBar, self).snapshot()
        snap['movable'] = self.movable
        snap['floatable'] = self.floatable
        snap['floating'] = self.floating
        snap['dock_area'] = self.dock_area
        snap['allowed_dock_areas'] = self.allowed_dock_areas
        return snap

    def bind(self):
        super(ToolBar, self).bind()
        attrs = (
            'movable', 'floatable', 'floating', 'dock_area', 
            'allowed_dock_areas'
        )
        self.publish_attributes(*attrs)

