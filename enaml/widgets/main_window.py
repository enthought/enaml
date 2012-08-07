#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .dock_pane import DockPane
from .window import Window


class MainWindow(Window):
    """ A top-level main window widget.

    MainWindow widgets are top-level widgets which provide various frame 
    decorations and other window related functionality. A window may 
    optionally contain a menubar, any number of toolbars, a status bar,
    and dock panes. A window can have at most one central widget child
    which will be expanded to fit the available space of the window.
    
    Sizing information relates to the size of the central widget rather
    than the overall size of the window. That is, specifying a minimum
    size for a MainWindow is akin to specifying a minimum size for the
    central widget. The space consumed by dock panes and menus is in
    addition to this space.

    """
    #: A read only property which returns the MenuBar in use for this
    #: MainWindow.
    # menu_bar = Property(depends_on='children[]')

    #: A read only property which returns the list of DockPanes in use
    #: for this MainWindow.
    dock_panes = Property(depends_on='children[]')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_dock_panes(self):
        """ The getter for the 'dock_panes' property.

        Returns
        -------
        result : list
            The list of dock panes in use on this MainWindow.

        """
        isinst = isinstance
        return [child for child in self.children if isinst(child, DockPane)]

    def _snap_dock_panes(self):
        """ Returns the serializable target ids for the dock panes.

        """
        return [pane.widget_id for pane in self.dock_panes]

    #--------------------------------------------------------------------------
    # Initialization 
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for a MainWindow.

        """
        snap = super(MainWindow, self).snapshot()
        snap['dock_panes'] = self._snap_dock_panes()
        return snap
    
