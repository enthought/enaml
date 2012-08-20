#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .constraints_widget import ConstraintsWidget
from .dock_pane import DockPane


class DockArea(ConstraintsWidget):
    """ A widget which can hold an arbitrary number of DockPanes.

    """
    #: A read only property which returns the area's dock panes.
    dock_panes = Property(depends_on='children[]')

    #: A DockArea expands freely in width and height by default.
    hug_width = 'ignore'
    hug_height = 'ignore'
    
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for a dock area.

        """
        snap = super(DockArea, self).snapshot()
        snap['dock_pane_ids'] = self._snap_dock_pane_ids()
        return snap

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_dock_panes(self):
        """ The getter for the 'dock_panes' property.

        Returns
        -------
        result : tuple
            The tuple of DockPane instances defined as children of this
            dock area.

        """
        isinst = isinstance
        panes = (child for child in self.children if isinst(child, DockPane))
        return tuple(panes)

    def _snap_dock_pane_ids(self):
        """ Return the widget ids of the area's dock panes.

        """
        return [pane.widget_id for pane in self.dock_panes]

