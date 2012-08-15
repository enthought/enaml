#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_action import wxAction, EVT_ACTION_CHANGED
from .wx_action_group import wxActionGroup
from .wx_constraints_widget import WxConstraintsWidget
from .wx_main_window import wxMainWindow


#: A mapping from Enaml dock orientation to wx dock position
_DOCK_AREA_MAP = {
    'left': wx.TB_LEFT,
    'right': wx.TB_RIGHT,
    'top': wx.TB_TOP,
    'bottom': wx.TB_BOTTOM,
}


#: A mapping from Enaml orientation to wx Orientation
_ORIENTATION_MAP = {
    'horizontal': wx.HORIZONTAL,
    'vertical': wx.VERTICAL,
}


class wxToolBar(wx.ToolBar):
    """ A wx.ToolBar subclass which handles wxAction instances.

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
        self.Bind(wx.EVT_MENU, self.OnMenu)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
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
        

    def OnMenu(self, event):
        """ The event handler for the EVT_MENU event.

        This handler maps the event to the appropriate wxAction.

        """
        print 'tb menu event'
        # action = wxAction.FindById(event.GetId())
        # if action is not None:
        #     if action.IsCheckable():
        #         action.SetChecked(event.Checked())
        #     action.Trigger()

    def OnActionChanged(self, event):
        """ The event handler for the EVT_ACTION_CHANGED event.

        This handler will be called when a child action changes. It
        ensures that the new state of the child action is in sync with
        the associated tool bar item.

        """
        # event.Skip()
        # action = event.GetEventObject()
        # item = self._actions_map.get(action)

        # # Fist, check for a visibility change. This requires adding or 
        # # removing the item from the tool bar and the actions map.
        # visible = action.IsVisible()
        # if visible != bool(item):
        #     if visible:
        #         new_item = self._CreationActionItem(action)
        #         index = self._all_items.index(action)
        #         index = min(index, len(self._actions_map))
        #         self.InsertItem(index, item)
        #         self._actions_map[action] = new_item
        #         self.Realize()
        #     else:
        #         self.DeleteTool(item.GetId())
        #         self.Realize()
        #         del self._actions_map[action]
        #     self.Refresh()
        #     return

        # # If the item is invisible, there is nothing to update.
        # if not item:
        #     return

        # # Handle a separator action.
        # if action.IsSeparator():
        #     item.SetKind(wx.ITEM_SEPARATOR)
        #     self.Refresh()
        #     return

        # # All other state is updated in-place
        # item.SetLabel(action.GetText())
        # item.SetShortHelp(action.GetToolTip())
        # item.SetLongHelp(action.GetStatusTip())
        # state = item.GetState()
        # if action.IsCheckable():
        #     item.SetKind(wx.ITEM_CHECK)
        #     if action.IsChecked():
        #         state |= aui.AUI_BUTTON_STATE_CHECKED
        #     else:
        #         state &= ~aui.AUI_BUTTON_STATE_CHECKED
        # else:
        #     state &= ~aui.AUI_BUTTON_STATE_CHECKED
        #     item.SetKind(wx.ITEM_NORMAL)
        # if not action.IsEnabled():
        #     state |= aui.AUI_BUTTON_STATE_DISABLED
        # else:
        #     state &= ~aui.AUI_BUTTON_STATE_DISABLED
        # item.SetState(state) 
        # self.Refresh()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
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
            bmp = wx.EmptyBitmap(0, 0)
            #bmp = wx.BitmapFromImage(wx.EmptyImage(1, 1))
            action_id = action.GetId()
            text = action.GetText()
            text = text or 'action_%d' % action_id
            if action.IsSeparator():
                self.AddSeparator()
            else:
                self.AddCheckLabelTool(action_id, text, bmp)
            #item = self._CreationActionItem(action)
            #self.AddItem(item)
            #self._actions_map[action] = item
            #action.Bind(EVT_ACTION_CHANGED, self.OnActionChanged)


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
        # The orientation or dock position of a tool bar can only be set
        # at creation time. Wx does not support changing it dynamically.
        style = wx.TB_TEXT
        if isinstance(parent, wxMainWindow):
            style |= _DOCK_AREA_MAP[tree['dock_area']]
        else:
            style |= _ORIENTATION_MAP[tree['orientation']]
    
        tbar = wxToolBar(parent, style=style)

        # Setting the tool bar to double buffered avoids a ton of
        # flickering on Windows during resize events.
        tbar.SetDoubleBuffered(True) 

        # For now, we set the bitmap size to 0 since we don't yet
        # support icons or images.
        tbar.SetToolBitmapSize(wx.Size(0, 0))

        return tbar

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
        # Wx does not support dynamically changing the orientation.
        pass

    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass

    def set_floating(self, floating):
        """ Set the floating staet on the underlying widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass

    def set_dock_area(self, dock_area):
        """ Set the dock area on the underyling widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        # The standard wx toolbar doesn't support docking. The Aui
        # toolbar sucks, don't use it.
        pass

