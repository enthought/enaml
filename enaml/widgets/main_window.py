#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .dock_pane import DockPane
from .tool_bar import ToolBar
from .window import Window


class MainWindow(Window):
    """ A top level main window widget.

    MainWindow widgets are top level widgets which provide additional
    functionality beyond frame decoration. A MainWindow may optionally
    contain a MenuBar, any number of ToolBars, a StatusBar, and any
    number of DockPanes. Like Window, a MainWindow can have at most one
    central Container widget, which will be expanded to fit into the 
    available space.

    """
    #: A read only property which returns the window's MenuBar.
    # menu_bar = Property(depends_on='children[]')

    #: A read only property which returns the window's ToolBars.
    tool_bars = Property(depends_on='children[]')

    #: A read only property which returns the window's DockPanes.
    dock_panes = Property(depends_on='children[]')

    #: A read only property which returns the window's StatusBar.
    # status_bar = Property(depends_on='children[]')

    #--------------------------------------------------------------------------
    # Initialization 
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot for the MainWindow.

        """
        snap = super(MainWindow, self).snapshot()
        snap['tool_bar_ids'] = self._snap_tool_bar_ids()
        snap['dock_pane_ids'] = self._snap_dock_pane_ids()
        return snap

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_tool_bars(self):
        """ The getter for the 'tool_bars' property.

        Returns
        -------
        result : tuple
            The tuple of ToolBar instances defined as children of this
            MainWindow.

        """
        isinst = isinstance
        panes = (child for child in self.children if isinst(child, ToolBar))
        return tuple(panes)

    @cached_property
    def _get_dock_panes(self):
        """ The getter for the 'dock_panes' property.

        Returns
        -------
        result : tuple
            The tuple of DockPane instances defined as children of this
            MainWindow.

        """
        isinst = isinstance
        panes = (child for child in self.children if isinst(child, DockPane))
        return tuple(panes)

    def _snap_tool_bar_ids(self):
        """ Returns the widget ids of the main window's tool bars.

        """
        return [bar.widget_id for bar in self.tool_bars]

    def _snap_dock_pane_ids(self):
        """ Returns the widget ids of the main window's dock panes.

        """
        return [pane.widget_id for pane in self.dock_panes]

