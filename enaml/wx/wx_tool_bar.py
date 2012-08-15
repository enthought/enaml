#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_action import wxAction, EVT_ACTION_CHANGED
from .wx_action_group import wxActionGroup
from .wx_constraints_widget import WxConstraintsWidget
from .wx_main_window import wxMainWindow
from .wx_upstream import aui


#: A mapping from Enaml dock areas to wx aui dock area enums
_DOCK_AREA_MAP = {
    'top': aui.AUI_DOCK_TOP,
    'right': aui.AUI_DOCK_RIGHT,
    'bottom': aui.AUI_DOCK_BOTTOM,
    'left': aui.AUI_DOCK_LEFT,
}

#: A mapping from wx aui dock area enums to Enaml dock areas.
_DOCK_AREA_INV_MAP = {
    aui.AUI_DOCK_TOP: 'top',
    aui.AUI_DOCK_RIGHT: 'right',
    aui.AUI_DOCK_BOTTOM: 'bottom',
    aui.AUI_DOCK_LEFT: 'left',
}

#: A mapping from Enaml allowed dock areas to wx direction enums.
_ALLOWED_AREAS_MAP = {
    'top': wx.TOP,
    'right': wx.RIGHT,
    'bottom': wx.BOTTOM,
    'left': wx.LEFT,
    'all': wx.ALL,
}

#: A mapping from Enaml orientation to wx Orientation
_ORIENTATION_MAP = {
    'horizontal': wx.HORIZONTAL,
    'vertical': wx.VERTICAL,
}


class wxToolBar(aui.AuiToolBar):
    """ An AuiToolBar subclass which handles wxAction instances.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxToolBar.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments needed to initialize
            an AuiToolBar.

        """
        super(wxToolBar, self).__init__(*args, **kwargs)
        self._all_items = []
        self._actions_map = {}
        self._movable = True
        self._floatable = True
        self._floating = False
        self._dock_area = aui.AUI_DOCK_LEFT
        self._allowed_dock_areas = wx.ALL
        self.Bind(wx.EVT_MENU, self.OnMenu)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _FindPaneManager(self):
        """ Find the pane manager for this tool bar.

        Returns
        -------
        result : AuiManager or None
            The AuiManager for this tool bar, or None if not found.
            If the tool bar is not a child of a wxMainWindow, then
            there will be no pane manager.

        """
        event = aui.AuiManagerEvent(aui.wxEVT_AUI_FIND_MANAGER)
        self.ProcessEvent(event)
        return event.GetManager()

    def _PaneInfoOperation(self, closure):
        """ A private method which will run the given closure if there 
        is a valid pane info object for this tool bar.

        """
        manager = self._FindPaneManager()
        if manager is not None:
            pane = manager.GetPane(self)
            if pane.IsOk():
                closure(pane)
                # Do some shenannigans to make sure the orientation and
                # and size of the toolbar is consistent. There shouldn't 
                # be a need to do this; this aui code is really bad...
                manager.SwitchToolBarOrientation(pane)
                pane.BestSize(self.GetClientSize())
                manager.Update()

    def _CreationActionItem(self, action):
        """ Create an AuiToolBarItem for the given action.

        Parameters
        ----------
        action : wxAction
            The wxAction instance for which create a tool bar item.

        Returns
        -------
        result : AuiToolBarItem
            The tool bar item instance to add to the toolbar.

        """
        item = aui.AuiToolBarItem()
        item.SetLabel(action.GetText())
        item.SetShortHelp(action.GetToolTip())
        item.SetLongHelp(action.GetStatusTip())
        item.SetId(action.GetId())

        state = item.GetState()

        if action.IsSeparator():
            item.SetKind(wx.ITEM_SEPARATOR)
        else:
            if action.IsCheckable():
                item.SetKind(wx.ITEM_CHECK)
                if action.IsChecked():
                    state |= aui.AUI_BUTTON_STATE_CHECKED
            else:
                item.SetKind(wx.ITEM_NORMAL)

        if not action.IsEnabled():
            state |= aui.AUI_BUTTON_STATE_DISABLED
        
        item.SetState(state)

        # Extra initing not dependent on the action.
        item.SetHasDropDown(False)
        item.SetSticky(False)
        item.SetOrientation(self._tool_orientation)
        return item

    def OnMenu(self, event):
        """ The event handler for the EVT_MENU event.

        This handler maps the event to the appropriate wxAction.

        """
        action = wxAction.FindById(event.GetId())
        if action is not None:
            if action.IsCheckable():
                action.SetChecked(event.Checked())
            action.Trigger()

    def OnActionChanged(self, event):
        """ The event handler for the EVT_ACTION_CHANGED event.

        This handler will be called when a child action changes. It
        ensures that the new state of the child action is in sync with
        the associated tool bar item.

        """
        event.Skip()
        action = event.GetEventObject()
        item = self._actions_map.get(action)

        # Fist, check for a visibility change. This requires adding or 
        # removing the item from the tool bar and the actions map.
        visible = action.IsVisible()
        if visible != bool(item):
            if visible:
                new_item = self._CreationActionItem(action)
                index = self._all_items.index(action)
                index = min(index, len(self._actions_map))
                self.InsertItem(index, item)
                self._actions_map[action] = new_item
                self.Realize()
            else:
                self.DeleteTool(item.GetId())
                self.Realize()
                del self._actions_map[action]
            self.Refresh()
            return

        # If the item is invisible, there is nothing to update.
        if not item:
            return

        # Handle a separator action.
        if action.IsSeparator():
            item.SetKind(wx.ITEM_SEPARATOR)
            self.Refresh()
            return

        # All other state is updated in-place
        item.SetLabel(action.GetText())
        item.SetShortHelp(action.GetToolTip())
        item.SetLongHelp(action.GetStatusTip())
        state = item.GetState()
        if action.IsCheckable():
            item.SetKind(wx.ITEM_CHECK)
            if action.IsChecked():
                state |= aui.AUI_BUTTON_STATE_CHECKED
            else:
                state &= ~aui.AUI_BUTTON_STATE_CHECKED
        else:
            state &= ~aui.AUI_BUTTON_STATE_CHECKED
            item.SetKind(wx.ITEM_NORMAL)
        if not action.IsEnabled():
            state |= aui.AUI_BUTTON_STATE_DISABLED
        else:
            state &= ~aui.AUI_BUTTON_STATE_DISABLED
        item.SetState(state) 
        self.Refresh()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def MakePaneInfo(self):
        """ Create a new AuiPaneInfo object for this tool bar.

        This is called by the wxMainWindow when it adds this tool bar
        to its internal layout for the first time.
        
        Returns
        -------
        result : AuiPaneInfo
            An initialized AuiPaneInfo object for this tool bar.

        """
        info = aui.AuiPaneInfo().ToolbarPane()

        info.Movable(self.GetMovable())
        info.Floatable(self.GetFloatable())
        info.Direction(self.GetDockArea())

        areas = self.GetAllowedDockAreas()
        info.TopDockable(bool(areas & wx.TOP))
        info.RightDockable(bool(areas & wx.RIGHT))
        info.LeftDockable(bool(areas & wx.LEFT))
        info.BottomDockable(bool(areas & wx.BOTTOM))

        if self.GetFloating():
            info.Float()
        else:
            info.Dock()

        return info

    def AddAction(self, action):
        """ Add an action to the tool bar.

        If the action is already owned by the toolbar, this is a no-op.

        Parameters
        ----------
        action : wxAction
            The wxAction instance to add to the tool bar.

        """
        all_items = self._all_items
        if action not in all_items:
            all_items.append(action)
            item = self._CreationActionItem(action)
            self.AddItem(item)
            self._actions_map[action] = item
            action.Bind(EVT_ACTION_CHANGED, self.OnActionChanged)

    def SetToolBarOrientation(self, orientation):
        """ Set the toolbar orientation.

        Set the orientation of the toolbar. This will take effect if the
        parent of the toolbar is not a wxMainWindow.

        """
        # This method is not named SetOrientation, because that exists 
        # on the superclass with a null implementation, yet that method
        # is still called by various methods on the parent class. So,
        # we just use a unique name to eliminate the confusion.
        if not isinstance(self.GetParent(), wxMainWindow):
            flags = self.GetAGWWindowStyleFlag()
            if orientation == wx.HORIZONTAL:
                flags &= ~aui.AUI_TB_VERTICAL
            else:
                flags |= aui.AUI_TB_VERTICAL
            self.SetAGWWindowStyleFlag(flags)

    def GetMovable(self):
        """ Get the movable state of the tool bar.

        Returns
        -------
        result : bool
            Whether or not the tool bar is movable.

        """
        return self._movable

    def SetMovable(self, movable):
        """ Set the movable state of the tool bar.

        This will only have an effect if this tool bar is a child of a
        wxMainWindow.

        Parameters
        ----------
        movable : bool
            Whether or not the tool bar is movable.

        """
        if self._movable != movable:
            self._movable = movable
            def closure(pane):
                pane.Movable(movable)
            self._PaneInfoOperation(closure)

    def GetFloatable(self):
        """ Get the floatable state of the tool bar.

        Returns
        -------
        result : bool
            Whether or not the tool bar is floatable.

        """
        return self._floatable

    def SetFloatable(self, floatable):
        """ Set the floatable state of the tool bar.

        This will only have an effect if this tool bar is a child of a
        wxMainWindow.

        Parameters
        ----------
        floatable : bool
            Whether or not the tool bar is floatable.

        """
        if self._floatable != floatable:
            self._floatable = floatable
            def closure(pane):
                pane.Floatable(floatable)
            self._PaneInfoOperation(closure)

    def GetFloating(self):
        """ Get the floating state of the tool bar.

        Returns
        -------
        result : bool
            Whether or not the tool bar is floating.

        """
        return self._floating

    def SetFloating(self, floating):
        """ Set the floating state of the tool bar.

        This will only have an effect if this tool bar is a child of a
        wxMainWindow.

        Parameters
        ----------
        floating : bool
            Whether or not the tool bar should be floating.

        """
        if self._floating != floating:
            self._floating = floating
            def closure(pane):
                if floating:
                    pane.Float()
                else:
                    pane.Dock()
            self._PaneInfoOperation(closure)

    def GetDockArea(self):
        """ Get the current dock area of the tool bar.

        Returns
        -------
        result : int
            The current dock area of the tool bar. One of the wx enums 
            LEFT, RIGHT, TOP, or BOTTOM.

        """
        return self._dock_area

    def SetDockArea(self, dock_area):
        """ Set the dock area for the tool bar.

        This will only have an effect if this tool bar is a child of a
        wxMainWindow.

        Parameters
        ----------
        dock_area : int
            The dock area for the tool bar. One of the wx enums LEFT, 
            RIGHT, TOP, or BOTTOM.

        """
        if self._dock_area != dock_area:
            self._dock_area = dock_area
            def closure(pane):
                pane.Direction(dock_area)
            self._PaneInfoOperation(closure)

    def GetAllowedDockAreas(self):
        """ Get the allowed dock areas for the tool bar.

        Returns
        -------
        result : int
            The allowed dock areas for the tool bar. One of the wx enums
            LEFT, RIGHT, TOP, BOTTOM, or ALL.

        """
        return self._allowed_dock_areas

    def SetAllowedDockAreas(self, dock_areas):
        """ Set the allowed dock areas for the tool bar.

        This will only have an effect if this tool bar is a child of a
        wxMainWindow.

        Parameters
        ----------
        dock_areas : int
            The allowed dock areas for the tool bar. One of the wx enums
            LEFT, RIGHT, TOP, BOTTOM, or ALL.

        """
        if self._allowed_dock_areas != dock_areas:
            self._allowed_dock_areas = dock_areas
            def closure(pane):
                pane.TopDockable(bool(dock_areas & wx.TOP))
                pane.RightDockable(bool(dock_areas & wx.RIGHT))
                pane.LeftDockable(bool(dock_areas & wx.LEFT))
                pane.BottomDockable(bool(dock_areas & wx.BOTTOM))
            self._PaneInfoOperation(closure)


class WxToolBar(WxConstraintsWidget):
    """ A Wx implementation of an Enaml ToolBar.

    """
    #: Storage for the tool bar item ids. 
    _item_ids = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying tool bar widget.

        """
        # Overflow is broken: checking an item on the overflow menu
        # doesn't emit any events, so keep it off.
        flags = aui.AUI_TB_TEXT #| aui.AUI_TB_OVERFLOW
        return wxToolBar(parent, agwStyle=flags)
    
    def create(self, tree):
        """ Create and initialize the underlying tool bar control.

        """
        super(WxToolBar, self).create(tree)
        self.set_item_ids(tree['item_ids'])
        self.set_orientation(tree['orientation'])
        self.set_movable(tree['movable'])
        self.set_floatable(tree['floatable'])
        self.set_floating(tree['floating'])
        self.set_dock_area(tree['dock_area'])
        self.set_allowed_dock_areas(tree['allowed_dock_areas'])

    def init_layout(self):
        """ Initialize the layout for the toolbar.

        """
        super(WxToolBar, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for item_id in self._item_ids:
            child = find_child(item_id)
            if child is not None:
                child_widget = child.widget()
                if isinstance(child_widget, wxAction):
                    widget.AddAction(child_widget)
                elif isinstance(child_widget, wxActionGroup):
                    for action in child_widget.GetActions():
                        widget.AddAction(action)
        # We must 'Realize()' the toolbar after adding items, or we
        # get exceptions for uninitialized state... We don't want 
        # this to be handled by the wxMainWindow, since the toolbar
        # can be used on its own.
        widget.Realize()

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_movable(self, content):
        """ Handle the 'set_movable' action from the Enaml widget.

        """
        self.set_movable(content['movable'])

    def on_action_set_floatable(self, content):
        """ Handle the 'set_floatable' action from the Enaml widget.

        """
        self.set_floatable(content['floatable'])

    def on_action_set_floating(self, content):
        """ Handle the 'set_floating' action from the Enaml widget.

        """
        self.set_floating(content['floating'])

    def on_action_set_dock_area(self, content):
        """ Handle the 'set_dock_area' action from the Enaml widget.

        """
        self.set_dock_area(content['dock_area'])

    def on_action_set_allowed_dock_areas(self, content):
        """ Handle the 'set_allowed_dock_areas' action from the Enaml
        widget.

        """
        self.set_allowed_dock_areas(content['allowed_dock_areas'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------\
    def set_visible(self, visible):
        """ Overridden parent class visibility setter which properly
        handles the visibility of the tool bar.

        """
        # XXX implement me!
        pass

    def set_item_ids(self, item_ids):
        """ Set the item ids for the underlying widget.

        """
        self._item_ids = item_ids

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        wx_orientation = _ORIENTATION_MAP[orientation]
        self.widget().SetToolBarOrientation(wx_orientation)

    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        self.widget().SetMovable(movable)

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        self.widget().SetFloatable(floatable)

    def set_floating(self, floating):
        """ Set the floating staet on the underlying widget.

        """
        self.widget().SetFloating(floating)

    def set_dock_area(self, dock_area):
        """ Set the dock area on the underyling widget.

        """
        self.widget().SetDockArea(_DOCK_AREA_MAP[dock_area])

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        wx_areas = 0
        for area in dock_areas:
            wx_areas |= _ALLOWED_AREAS_MAP[area]
        self.widget().SetAllowedDockAreas(wx_areas)

