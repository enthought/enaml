#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from enaml.core.trait_types import EnamlEvent

from .dock_pane import DockPane
from .window import Window


class MainWindow(Window):
    """ A top level main window widget.

    MainWindow widgets are top level widgets which provide additional
    functionality beyond frame decoration. A MainWindow may optionally
    contain a MenuBar, any number of ToolBars, a StatusBar, and any
    number of DockPanes. Like Window, a MainWindow can have at most one
    central Container widget, which will be expanded to fit int the 
    available space.

    """
    #: A read only property which returns the window's MenuBar.
    # menu_bar = Property(depends_on='children[]')

    #: A read only property which returns the window's StatusBar.
    # status_bar = Property(depends_on='children[]')

    #: A read only property which returns the window's ToolBars.
    # tool_bars = Property(depends_on='children[]')

    #: A read only property which returns the window's DockPanes.
    dock_panes = Property(depends_on='children[]')

    #: An event fired when the user closes a dock pane by clicking on 
    #: its close button. The content will be the dock pane object.
    dock_pane_closed = EnamlEvent

    #--------------------------------------------------------------------------
    # Initialization 
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot for the MainWindow.

        """
        snap = super(MainWindow, self).snapshot()
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
        result : list
            The list of DockPane instances defined as children of this
            MainWindow.

        """
        isinst = isinstance
        panes = (child for child in self.children if isinst(child, DockPane))
        return tuple(panes)

    def _snap_dock_pane_ids(self):
        """ Returns the widget ids of window's dock panes.

        """
        return [pane.widget_id for pane in self.dock_panes]
    
    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_dock_pane_closed(self, content):
        """ Handle the 'dock_pane_closed' action from the client widget.

        """
        widget_id = content['widget_id']
        for dock_pane in self.dock_panes:
            if dock_pane.widget_id == widget_id:
                self.dock_pane_closed(dock_pane)
                dock_pane.closed()
                return

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open_dock_pane(self, dock_pane):
        """ Open the given dock pane if it isn't already open.

        Parameters
        ----------
        dock_pane : DockPane
            The DockPane instance to open. It must be a child of this 
            MainWindow.

        """
        if dock_pane not in self.dock_panes:
            msg = 'DockPane is not a child of the MainWindow'
            raise ValueError(msg)
        content = {'widget_id': dock_pane.widget_id}
        self.send_action('open_dock_pane', content)

    def close_dock_pane(self, dock_pane):
        """ Close the given dock pane if it isn't already open.

        Parameters
        ----------
        dock_pane : DockPane
            The DockPane instance to close. It must be a child of this 
            MainWindow.

        """
        if dock_pane not in self.dock_panes:
            msg = 'DockPane is not a child of the MainWindow'
            raise ValueError(msg)
        content = {'widget_id': dock_pane.widget_id}
        self.send_action('close_dock_pane', content)

