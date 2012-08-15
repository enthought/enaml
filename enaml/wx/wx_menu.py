#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_action import wxAction, EVT_ACTION_CHANGED
from .wx_action_group import wxActionGroup
from .wx_widget_component import WxWidgetComponent


#: An event emitted when the menu state changes.
wxMenuChangedEvent, EVT_MENU_CHANGED = wx.lib.newevent.NewEvent()


class wxMenu(wx.Menu):
    """ A wx.Menu subclass which provides a more convenient api for
    working with wxMenu and wxAction children.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxMenu.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wx.Menu.

        """
        super(wxMenu, self).__init__(*args, **kwargs)
        self._title = u''
        self._all_items = []
        self._menus_map = {}
        self._actions_map = {}
        self._enabled = True
        self._bar_enabled = True
        self._visible = True
        self._batch = False
        self._id = wx.NewId()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _EmitChanged(self):
        """ Emits the menu changed event if not in batch mode.

        """
        if not self._batch:
            event = wxMenuChangedEvent()
            event.SetEventObject(self)
            wx.PostEvent(self, event)

    def _SetBarEnabled(self, enabled):
        """ A private method called by an owner menu bar.

        Parameters
        ----------
        enabled : bool
            Whether or not the owner menu bar is enabled.

        """
        if self._bar_enabled != enabled:
            old = self.IsEnabled()
            self._bar_enabled = enabled
            new = self.IsEnabled()
            if old != new:
                self._EmitChanged()

    def _CreateMenuItem(self, menu):
        """ Create a menu item for the given menu.

        Parameters
        ----------
        menu : wxMenu
            The wxMenu instance to use as the submenu.

        Returns
        -------
        result : wx.MenuItem
            The menu item to use for the given menu.

        """
        text = menu.GetTitle()
        menu_id = menu.GetId()
        text = text or 'menu_%d' % menu_id # null text == exception 
        res = wx.MenuItem(self, menu_id, text, '', subMenu=menu)
        res.Enable(menu.IsEnabled())
        return res

    def _CreateActionItem(self, action):
        """ Create a menu item for the given action.

        Parameters
        ----------
        action : wxAction
            The wx action for which to create a wx.MenuItem.

        Returns
        -------
        result : wx.MenuItem
            The menu item for the given action.

        """
        text = action.GetText()
        help = action.GetStatusTip()
        if action.IsSeparator():
            res = wx.MenuItem(self, wx.ID_SEPARATOR, text, help)
        else:
            action_id = action.GetId()
            text = text or 'action_%d' % action_id # null text == exception
            if action.IsCheckable():
                # The wx.ITEM_RADIO kind doesn't behave nicely, so we
                # just use the check kind and rely on the action group
                # to handle the exclusive radio behavior. Changing the 
                # bitmap to something that looks like a radio button 
                # breaks the Windows theme.
                kind = wx.ITEM_CHECK
                res = wx.MenuItem(self, action_id, text, help, kind)
                res.Check(action.IsChecked())
            else:
                kind = wx.ITEM_NORMAL
                res = wx.MenuItem(self, action_id, text, help, kind)
            res.Enable(action.IsEnabled())
        return res

    def OnActionChanged(self, event):
        """ The event handler for the EVT_ACTION_CHANGED event.

        This handler will be called when a child action changes. It
        ensures that the new state of the child action is in sync with
        the associated menu item.

        """
        event.Skip()
        action = event.GetEventObject()
        item = self._actions_map.get(action)

        # Fist, check for a visibility change. This requires adding or 
        # removing the menu item from the menu and the actions map.
        visible = action.IsVisible()
        if visible != bool(item):
            if visible:
                new_item = self._CreateActionItem(action)
                index = self._all_items.index(action)
                n_visible = len(self._actions_map) + len(self._menus_map)
                index = min(index, n_visible)
                self.InsertItem(index, new_item)
                self._actions_map[action] = new_item
            else:
                self.DestroyItem(item)
                del self._actions_map[action]
            return

        # If the item is invisible, there is nothing to update.
        if not item:
            return

        # If the item is a separator, and the separator state has 
        # changed, we need to build an entirely new menu item, and
        # replace the existing item with the new one.
        item_sep = item.IsSeparator()
        action_sep = action.IsSeparator()
        if item_sep or action_sep:
            if item_sep != action_sep:
                self.DestroyItem(item)
                new_item = self._CreateActionItem(action)
                index = self._all_items.index(action)
                self.InsertItem(index, new_item)
                self._actions_map[action] = new_item
            return

        # For all other state, the menu item can be updated in-place.
        item.SetItemLabel(action.GetText())
        item.SetHelp(action.GetStatusTip())
        if item.IsCheckable():
            item.Check(action.IsChecked())
        item.Enable(action.IsEnabled())

    def OnMenuChanged(self, event):
        """ The event hanlder for the EVT_MENU_CHANGED event.

        This handler will be called when a child menu changes. It
        ensure that the new state of the child menu is in sync with
        the associated menu item.

        """
        event.Skip()
        menu = event.GetEventObject()
        item = self._menus_map.get(menu)

        # Fist, check for a visibility change. This requires adding or 
        # removing the menu item from the menu and the menus map.
        visible = menu.IsVisible()
        if visible != bool(item):
            if visible:
                new_item = self._CreateMenuItem(menu)
                index = self._all_items.index(menu)
                n_visible = len(self._actions_map) + len(self._menus_map)
                index = min(index, n_visible)
                self.InsertItem(index, new_item)
                self._menus_map[menu] = new_item
            else:
                # Need to first remove the submenu or wx will destroy it.
                item.SetSubMenu(None)
                self.DestroyItem(item)
                del self._menus_map[menu]
            return

        # If the item is invisible, there is nothing to update.
        if not item:
            return

        # For all other state, the menu item can be updated in-place.
        item.SetItemLabel(menu.GetTitle())
        item.Enable(menu.IsEnabled())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def BeginBatch(self):
        """ Enter batch update mode for the menu.

        """
        self._batch = True

    def EndBatch(self, emit=True):
        """ Exit batch update mode for the menu.

        Parameters
        ----------
        emit : bool, optional
            If True, emit a changed event after leaving batch mode. The
            default is True.

        """
        self._batch = False
        if emit:
            self._EmitChanged()

    def GetId(self):
        """ Get the unique wx id for this menu.

        Returns
        -------
        result : int
            The wx id number for this menu.

        """
        return self._id

    def GetTitle(self):
        """ Get the title for the menu.

        Returns
        -------
        result : unicode
            The unicode title for the menu.

        """
        return self._title

    def SetTitle(self, title):
        """ Set the title for the menu.

        Parameters
        ----------
        title : unicode
            The unicode string to use as the menu title.

        """
        if self._title != title:
            self._title = title
            self._EmitChanged()

    def IsEnabled(self):
        """ Get whether or not the menu is enabled.

        Returns
        -------
        result : bool
            Whether or not the menu is enabled.

        """
        if self._bar_enabled:
            return self._enabled
        return False

    def SetEnabled(self, enabled):
        """ Set whether or not the menu is enabled.

        Parameters
        ----------
        enabled : bool
            Whether or not the menu is enabled.

        """
        if self._enabled != enabled:
            self._enabled = enabled
            if self._bar_enabled:
                self._EmitChanged()

    def IsVisible(self):
        """ Get whether or not the menu is visible.

        Returns
        -------
        result : bool
            Whether or not the menu is visible.

        """
        return self._visible

    def SetVisible(self, visible):
        """ Set whether or not the menu is visible.

        Parameters
        ----------
        visible : bool
            Whether or not the menu is visible.

        """
        if self._visible != visible:
            self._visible = visible
            self._EmitChanged()

    def AddMenu(self, menu):
        """ Add a wx menu to the Menu.

        If the menu already exists in this menu, this is a no-op.

        Parameters
        ----------
        menu : wxMenu
            The wxMenu instance to add to this menu.

        """
        menus_map = self._menus_map
        if menu not in menus_map:
            self._all_items.append(menu)
            if menu.IsVisible():
                menu_item = self._CreateMenuItem(menu)
                menus_map[menu] = menu_item
                self.AppendItem(menu_item)
            menu.Bind(EVT_MENU_CHANGED, self.OnMenuChanged)

    def AddAction(self, action):
        """ Add a wx action to the Menu.

        If the action already exists in the menu, this is a no-op.

        Parameters
        ----------
        action : wxAction
            The wxAction instance ot add to this menu.

        """
        actions_map = self._actions_map
        if action not in actions_map:
            self._all_items.append(action)
            if action.IsVisible():
                menu_item = self._CreateActionItem(action)
                actions_map[action] = menu_item
                self.AppendItem(menu_item)
            action.Bind(EVT_ACTION_CHANGED, self.OnActionChanged)


class WxMenu(WxWidgetComponent):
    """ A Wx implementation of an Enaml Menu.

    """
    #: Storage for the menu item ids
    _menu_item_ids = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx menu widget.

        """
        widget = wxMenu()
        widget.BeginBatch()
        return widget

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(WxMenu, self).create(tree)
        self.set_menu_item_ids(tree['menu_item_ids'])
        self.set_title(tree['title'])
        self.widget().EndBatch(emit=False)

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(WxMenu, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for item_id in self._menu_item_ids:
            child = find_child(item_id)
            if child is not None:
                child_widget = child.widget()
                if isinstance(child_widget, wxMenu):
                    widget.AddMenu(child_widget)
                elif isinstance(child_widget, wxAction):
                    widget.AddAction(child_widget)
                elif isinstance(child_widget, wxActionGroup):
                    for action in child_widget.GetActions():
                        widget.AddAction(action)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_menu_item_ids(self, menu_item_ids):
        """ Set the menu item ids of the underlying control.

        """
        self._menu_item_ids = menu_item_ids

    def set_title(self, title):
        """ Set the title of the underlyling control.

        """
        self.widget().SetTitle(title)

    def set_enabled(self, enabled):
        """ Overridden parent class method.

        This properly sets the enabled state on a menu using the custom
        wxMenu api.

        """
        self.widget().SetEnabled(enabled)

    def set_visible(self, visible):
        """ Overrdden parent class method.

        This properly sets the visible state on a menu using the custom
        wxMenu api.

        """
        self.widget().SetVisible(visible)

    def set_minimum_size(self, min_size):
        """ Overridden parent class method.

        Menus do not have a minimum size, so this method is a no-op.

        """
        pass

    def set_maximum_size(self, max_size):
        """ Overridden parent class method.

        Menus do not have a maximum size, so this method is a no-op.

        """
        pass

