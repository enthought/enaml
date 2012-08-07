#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.aui

from .wx_window import WxWindow


class wxMainWindow(wx.Frame):
    """ A wx.Frame subclass which behaves like a MainWindow.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxMainWindow.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments necessary to initialize
            a wx.Frame.

        """
        super(wxMainWindow, self).__init__(*args, **kwargs)
        self._central_widget = None
        self._pane_manager = wx.aui.AuiManager(self)
        self._dock_panes = set()
        self._pause_updates = False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _InitPaneInfo(self, dock_pane):
        """ Create and initialize an AuiPaneInfo for the dock pane.

        Parameters
        ----------
        dock_pane : wxDockPane
            The wxDockPane instance for which to create the pane info.

        Returns
        -------
        result : AuiPaneInfo
            A new pane info instance configured for the current state
            of the dock pane.

        """
        info = wx.aui.AuiPaneInfo()
        best_size = dock_pane.GetBestSize()
        min_size = dock_pane.GetEffectiveMinSize()
        info.BestSize(best_size).MinSize(min_size)
        return info

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def BeginBatch(self):
        """ Enter batch update mode for pane updates.

        Pane updates that are performed after calling this method will
        not be committed until EndBatch is called.

        """
        self._pause_updates = True

    def EndBatch(self):
        """ Exit batch update mode and any pending pane updates.

        """
        self._pause_updates = False
        self._pane_manager.Update()

    def SetCentralWidget(self, widget):
        """ Set the central widget for the main window.

        Parameters
        ----------
        widget : wxWindow
            The wxWindow instance to use as the central widget in the
            main window.

        """
        # XXX remove old central widget
        self._central_widget = widget
        pane = wx.aui.AuiPaneInfo().CenterPane()
        self._pane_manager.AddPane(widget, pane)
        if not self._pause_updates:
            self._pane_manager.Update()

    def AddDockPane(self, dock_pane):
        """ Add a dock pane to the main window.

        If the pane already exists in the main window, calling this 
        method is a no-op.

        Parameters
        ----------
        dock_pane : wxDockPane
            The wxDockPane instance to add to the main window.

        """
        if dock_pane in self._dock_panes:
            return
        self._dock_panes.add(dock_pane)

        pane_manager = self._pane_manager
        if pane_manager.GetPane(dock_pane).IsOk():
            return

        title = dock_pane.GetTitle()
        info = self._InitPaneInfo(dock_pane)
        pane_manager.AddPane(dock_pane, info, title)
        
        if not self._pause_updates:
            pane_manager.Update()

    def RemoveDockPane(self, dock_pane):
        """ Remove a dock pane from the main window.

        If the pane does not exist in the window, calling this method
        is a no-op.

        Parameters
        ----------
        dock_pane : wxDockPane
            The wxDockPane instance to remove from the window.

        """
        pass


class WxMainWindow(WxWindow):
    """ A Wx implementation of an Enaml MainWindow.

    """
    #: Storage for a dummy widget for the case where there are no dock
    #: panes specified. This works around an issue in wx where the layout
    #: will jitter on resize if only a central pane is present.
    _dummy_widget = None

    #: Storage for the widget ids of the dock panes
    _dock_panes = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx.Frame widget and dock manager.

        """
        return wxMainWindow(parent)

    def create(self, tree):
        """ Create and initialize the main window control.

        """
        super(WxMainWindow, self).create(tree)
        self.set_dock_panes(tree['dock_panes'])

    def init_layout(self):
        """ Perform the layout initialization for the main window.

        """
        main_window = self.widget

        # Build a mapping of widget_id -> child. This saves us from 
        # doing multiple O(n) lookups in the following operations.
        child_map = dict((child.widget_id, child) for child in self.children)

        main_window.BeginBatch()

        # Setup the central widget
        central_child = child_map.get(self._central_widget)
        if central_child is not None:
            main_window.SetCentralWidget(central_child.widget)

        # Setup the dock panes
        for dock_id in self._dock_panes:
            dock_pane = child_map.get(dock_id)
            if dock_pane is not None:
                main_window.AddDockPane(dock_pane.widget)

        main_window.EndBatch()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_dock_panes(self, panes):
        """ Set the dock panes for the underlying widget.

        """
        self._dock_panes = panes

