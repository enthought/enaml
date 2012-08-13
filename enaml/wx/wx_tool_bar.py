#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import count

import wx

from .wx_action import EVT_ACTION_CHANGED
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
        self._actions = []
        self._tool_item_map = {}
        self._tool_id_gen = count()
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

    def OnMenu(self, event):
        """ The event handler for the EVT_MENU event.

        This handler calls the appropriate triggered and toggled methods
        on the underlying action, in the same order as peformed by Qt.

        """
        # If the clicked item is a radio button that has been toggled,
        # we first emit it's toggled event, followed by the toggle off
        # event for its siblings. After all toggle events are fired, 
        # the triggered event is fired. Wx does not give us a toggle
        # off event, so we need to do a linear search and fire one 
        # off ourselves for any control that has changed state.
        tool_item_map = self._tool_item_map
        check_flag = aui.AUI_BUTTON_STATE_CHECKED
        tool_id = event.GetId()
        tool_item = self.FindTool(tool_id)
        action = tool_item_map[tool_item]
        checked = bool(tool_item.state & check_flag)
        if checked != action.IsChecked():
            action.ActionToggled(checked)
            if tool_item.kind == wx.ITEM_RADIO:
                for other_item, other_action in tool_item_map.iteritems():
                    if other_action is not action:
                        item_checked = bool(other_item.state & check_flag)
                        if item_checked != other_action.IsChecked():
                            other_action.ActionToggled(item_checked)
        action.ActionTriggered()

    def OnActionChanged(self, event):
        """ The event handler for the EVT_ACTION_CHANGED event.

        This handler update the state of the given action in the toolbar.

        """
        # XXX implement me!
        pass

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
        # If the action already exists in this toolbar, bail early.
        actions = self._actions
        if action in actions:
            return
        actions.append(action)

        # Grab the data from the action that's needed to add the item
        # to the toolbar and build the corresponding tool item.
        if action.IsSeparator():
            tool_item = self.AddSeparator()
        else:
            tool_id = self._tool_id_gen.next()
            text = action.GetText()
            if action.IsCheckable():
                if action.IsExclusive():
                    kind = wx.ITEM_RADIO
                else:
                    kind = wx.ITEM_CHECK
            else:
                kind = wx.ITEM_NORMAL
            bmp = wx.NullBitmap
            tool_item = self.AddSimpleTool(tool_id, text, bmp, kind=kind)

        # Store away a reference to the tool item so we map it back
        # to the action for event handling purposes.
        self._tool_item_map[tool_item] = action

        # Finally, bind the change handler for the action so that we
        # can update the tool item when the action changes.
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
    #: Storage for the action ids
    _action_ids = []

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
        self.set_action_ids(tree['action_ids'])
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
        for action_id in self._action_ids:
            child = find_child(action_id)
            if child is not None:
                widget.AddAction(child.widget())
        # We must 'Realize()' the toolbar after adding items, or we
        # get exceptions for uninitialized state...
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
        # XXX implement me!
        pass

    def set_action_ids(self, action_ids):
        """ Set the action ids for the underlying widget.

        """
        self._action_ids = action_ids

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

