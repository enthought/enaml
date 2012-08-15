#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_action import wxAction
from .wx_upstream import aui
from .wx_window import WxWindow


class wxMainWindow(wx.Frame):
    """ A wx.Frame subclass which adds MainWindow functionality.

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
        flags = (
            aui.AUI_MGR_DEFAULT | aui.AUI_MGR_LIVE_RESIZE | 
            aui.AUI_MGR_USE_NATIVE_MINIFRAMES
        )
        self._manager = aui.AuiManager(self, agwFlags=flags)
        self._central_widget = None
        self._batch = False
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)
        self.Bind(aui.EVT_AUI_PANE_FLOATED, self.OnPaneFloated)
        self.Bind(aui.EVT_AUI_PANE_DOCKED, self.OnPaneDocked)

        # Add a hidden dummy widget to the pane manager. This is a 
        # workaround for a Wx bug where the laying out of the central
        # pane will have jitter on window resize (the computed layout
        # origin of the central pane oscillates between (0, 0) and 
        # (1, 1)) if there are no other panes in the layout. If we 
        # add a hidden pane with zero size, it prevents the jitter.
        self._hidden_widget = wx.Window(self)
        pane = aui.AuiPaneInfo()
        pane.BestSize(wx.Size(0, 0))
        pane.MinSize(wx.Size(0, 0))
        pane.Show(False)
        self._manager.AddPane(self._hidden_widget, pane)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnPaneClose(self, event):
        """ Handle the EVT_AUI_PANE_CLOSE event.

        This event gets passed on to the wxDockPane for handling.

        """
        event.GetPane().window.OnClose(event)

    def OnPaneFloated(self, event):
        """ Handle the EVT_AUI_PANE_FLOATED event.

        This event gets passed on to the wxDockPane for handling.

        """
        event.GetPane().window.OnFloated(event)

    def OnPaneDocked(self, event):
        """ Handle the EVT_AUI_PANE_DOCKED event.

        This event gets passed on to the wxDockPane for handling.

        """
        event.GetPane().window.OnDocked(event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetAuiManager(self):
        """ Get the pane manager for the main window.

        This method should not normally be called by the user. It is
        used by the various children of the main window when they need
        to manipulate the state of their pane info object.

        Returns
        -------
        result : AuiManager
            The AuiManager instance managing the panes for this window.

        """
        return self._manager

    def BeginBatch(self):
        """ Enter batch update mode for main window updates.

        Main window updates that are performed after calling this method
        will not be committed until EndBatch is called. This can be used
        to reduce flicker when making updates to the MainWindow.

        """
        self._batch = True

    def EndBatch(self):
        """ Exit batch update mode and process any pending updates.

        After calling this method, any pending main window updates will
        be processed.

        """
        self._batch = False
        self._manager.Update()

    def SetCentralWidget(self, widget):
        """ Set the central widget for the main window.

        Parameters
        ----------
        widget : wxWindow
            The wxWindow instance to use as the central widget in the
            main window.

        """
        manager = self._manager
        
        old_widget = self._central_widget
        if old_widget:
            pane = manager.GetPane(old_widget)
            if pane.IsOk():
                pane.Show(False)
                manager.DetachPane(old_widget)

        self._central_widget = widget
        pane = aui.AuiPaneInfo().CenterPane()
        manager.AddPane(widget, pane)

        if not self._batch:
            manager.Update()

    def AddToolBar(self, tool_bar):
        """ Add a tool bar to the main window.

        If the tool bar already exists in the main window, calling this
        method is a no-op.

        Parameters
        ----------
        tool_bar : wxToolBar
            The wxToolBar instance to add to the main window.

        """
        manager = self._manager
        pane = manager.GetPane(tool_bar)
        if not pane.IsOk():
            pane = tool_bar.MakePaneInfo()
            # Do some shennanigans to make sure the toolbar is oriented
            # properly on initial display. There shouldn't be a need to
            # do this; this aui code is really bad...
            pane.Window(tool_bar)
            manager.SwitchToolBarOrientation(pane)
            manager.AddPane(tool_bar, pane)
            if not self._batch:
                manager.Update()

    def AddDockPane(self, dock_pane):
        """ Add a dock pane to the main window.

        If the pane already exists in the main window, calling this 
        method is a no-op.

        Parameters
        ----------
        dock_pane : wxDockPane
            The wxDockPane instance to add to the main window.

        """
        manager = self._manager
        pane = manager.GetPane(dock_pane)
        if not pane.IsOk():
            manager.AddPane(dock_pane, dock_pane.MakePaneInfo())
            if not self._batch:
                manager.Update()

    def RemoveDockPane(self, dock_pane):
        """ Remove a dock pane from the main window.

        If the pane does not exist in the window, calling this method
        is a no-op.

        Parameters
        ----------
        dock_pane : wxDockPane
            The wxDockPane instance to remove from the window.

        """
        manager = self._manager
        pane = manager.GetPane(dock_pane)
        if pane.IsOk():
            pane.Show(False)
            manager.DetachPane(dock_pane)
            if not self._batch:
                manager.Update()


class WxMainWindow(WxWindow):
    """ A Wx implementation of an Enaml MainWindow.

    """
    #: Storage for the menu bar id
    _menu_bar_id = None

    #: Storage for the widget ids of the dock panes
    _dock_pane_ids = []

    #: Storage for the widget ids of the tool bars
    _tool_bar_ids = []

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
        self.set_menu_bar_id(tree['menu_bar_id'])
        self.set_dock_pane_ids(tree['dock_pane_ids'])
        self.set_tool_bar_ids(tree['tool_bar_ids'])
        self.widget().Bind(wx.EVT_MENU, self.OnMenu)

    def OnMenu(self, event):
        action = wxAction.FindById(event.GetId())
        if action is not None:
            if action.IsCheckable():
                action.SetChecked(event.Checked())

    def init_layout(self):
        """ Perform the layout initialization for the main window.

        """
        # The superclass' init_layout() method is explicitly not called
        # since the layout initialization for Window is not appropriate
        # for MainWindow
        main_window = self.widget()
        find_child = self.find_child

        main_window.BeginBatch()

        # Setup the menu bar
        menu_bar = find_child(self._menu_bar_id)
        if menu_bar is not None:
            main_window.SetMenuBar(menu_bar.widget())
            # The menu bar must be refreshed after attachment
            menu_bar.widget().Update()

        # Setup the central widget
        central_child = find_child(self._central_widget_id)
        if central_child is not None:
            main_window.SetCentralWidget(central_child.widget())

        # Setup the tool bars
        for tool_bar_id in self._tool_bar_ids:
            tool_bar = find_child(tool_bar_id)
            if tool_bar is not None:
                main_window.AddToolBar(tool_bar.widget())

        # Setup the dock panes
        for dock_id in self._dock_pane_ids:
            dock_pane = find_child(dock_id)
            if dock_pane is not None:
                main_window.AddDockPane(dock_pane.widget())

        # Setup the status bar
        self._status = status = wx.StatusBar(main_window)
        main_window.SetStatusBar(status)
        
        main_window.EndBatch()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_menu_bar_id(self, menu_bar_id):
        """ Set the menu bar id for the underlying widget.

        """
        self._menu_bar_id = menu_bar_id

    def set_dock_pane_ids(self, pane_ids):
        """ Set the dock pane ids for the underlying widget.

        """
        self._dock_pane_ids = pane_ids

    def set_tool_bar_ids(self, bar_ids):
        """ Set the tool bar ids for the underlying widget.

        """
        self._tool_bar_ids = bar_ids

