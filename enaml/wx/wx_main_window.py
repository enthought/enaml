#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.aui
import wx.lib.newevent

from .wx_window import WxWindow


#: An event emitted when a main window pane is closed. The event will
#: have an attribute 'DockPane' which is the dock pane which was closed.
wxDockPaneClosedEvent, EVT_DOCK_PANE_CLOSED = wx.lib.newevent.NewEvent()


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
        self._pane_manager = wx.aui.AuiManager(self)
        self._central_widget = None
        self._batch = False
        self.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self._OnPaneClose)

        # Add a hidden dummy widget to the pane manager. This is a 
        # workaround for a Wx bug where the laying out of the central
        # pane will have jitter on window resize (the computed layout
        # origin of the central pane oscillates between (0, 0) and 
        # (1, 1)) if there are no other panes in the layout. If we 
        # add a hidden pane with zero size, it prevents the jitter.
        self._hidden_widget = wx.Window(self)
        pane = wx.aui.AuiPaneInfo()
        pane.BestSize(wx.Size(0, 0)).MinSize(wx.Size(0, 0)).Show(False)
        self._pane_manager.AddPane(self._hidden_widget, pane)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _OnPaneClose(self, event):
        """ Handle the EVT_AUI_PANE_CLOSE event.

        Wx does not reliably toggle the close button dynamically when 
        setting the CloseButton flag on the PaneInfo object for the 
        dock pane, so we always display the button, and veto the close 
        event when appropriate.

        """
        info = event.GetPane()
        dock_pane = info.window
        if not dock_pane.GetClosable():
            event.Veto()
        else:
            # If the event is Skipped, wx will call this handler twice. 
            # Hence, don't skip the event.
            evt = wxDockPaneClosedEvent(DockPane=dock_pane)
            wx.PostEvent(self, evt)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
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
        self._pane_manager.Update()

    def SetCentralWidget(self, widget):
        """ Set the central widget for the main window.

        Parameters
        ----------
        widget : wxWindow
            The wxWindow instance to use as the central widget in the
            main window.

        """
        manager = self._pane_manager
        
        old_widget = self._central_widget
        if old_widget:
            pane = manager.GetPane(old_widget)
            if pane.IsOk():
                pane.Show(False)
                manager.DetachPane(old_widget)

        self._central_widget = widget
        pane = wx.aui.AuiPaneInfo().CenterPane()
        manager.AddPane(widget, pane)

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
        manager = self._pane_manager
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
        manager = self._pane_manager
        pane = manager.GetPane(dock_pane)
        if pane.IsOk():
            pane.Show(False)
            manager.DetachPane(dock_pane)
            if not self._batch:
                manager.Update()

    def OpenDockPane(self, dock_pane):
        """ Unhide the given dock pane in the main window.

        If the pane does not exist in the window, this is a no-op.

        Parameters
        ----------
        dock_pane : wxDockPane
            The wxDockPane instance to open in the window.

        """
        manager = self._pane_manager
        pane = manager.GetPane(dock_pane)
        if pane.IsOk():
            pane.Show(True)
            if not self._batch:
                manager.Update()

    def CloseDockPane(self, dock_pane):
        """ Hide the given dock pane in the main window.

        If the pane does not exist in the window, this is a no op.

        Parameters
        ----------
        dock_pane : wxDockPane
            The wxDockPane instance to close in the window.

        """
        manager = self._pane_manager
        pane = manager.GetPane(dock_pane)
        if pane.IsOk():
            pane.Show(False)
            if not self._batch:
                manager.Update()

    def GetPaneManager(self):
        """ Get the pane manager for the main window.

        This method should not normally be called by the user. It is
        used by the various children of the main window when they need
        to manipulate the state of their pane info object.

        Returns
        -------
        result : AuiManager
            The AuiManager instance managing the panes for this window.

        """
        return self._pane_manager


class WxMainWindow(WxWindow):
    """ A Wx implementation of an Enaml MainWindow.

    """
    #: Storage for the widget ids of the dock panes
    _dock_pane_ids = []

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
        self.set_dock_pane_ids(tree['dock_pane_ids'])
        self.widget.Bind(EVT_DOCK_PANE_CLOSED, self.on_dock_pane_closed)

    def init_layout(self):
        """ Perform the layout initialization for the main window.

        """
        # The superclass' init_layout() method is explicitly not called
        # since the layout initialization for Window is not appropriate
        # for MainWindow
        main_window = self.widget
        children_map = self.children_map

        main_window.BeginBatch()

        # Setup the central widget
        central_child = children_map.get(self._central_widget)
        if central_child is not None:
            main_window.SetCentralWidget(central_child.widget)

        # Setup the dock panes
        for dock_id in self._dock_pane_ids:
            dock_pane = children_map.get(dock_id)
            if dock_pane is not None:
                main_window.AddDockPane(dock_pane.widget)

        main_window.EndBatch()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_dock_pane_closed(self, event):
        """ The event handler for the EVT_DOCK_PANE_CLOSED event.

        """
        dock_pane = event.DockPane
        for child in self.children:
            if dock_pane == child.widget:
                widget_id = child.widget_id
                content = {'widget_id': widget_id}
                self.send_action('dock_pane_closed', content)
                return

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_open_dock_pane(self, content):
        """ Handle the 'open_dock_pane' action from the Enaml widget.

        """
        child = self.children_map.get(content.widget_id)
        if child is not None:
            self.widget.OpenDockPane(child.widget)

    def on_action_close_dock_pane(self, content):
        """ Handle the 'close_dock_pane' action from the Enaml widget.

        """
        child = self.children_map.get(content.widget_id)
        if child is not None:
            self.widget.CloseDockPane(child.widget)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_dock_pane_ids(self, pane_ids):
        """ Set the dock pane ids for the underlying widget.

        """
        self._dock_pane_ids = pane_ids

