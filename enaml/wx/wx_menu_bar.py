#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_menu import EVT_MENU_CHANGED
from .wx_widget_component import WxWidgetComponent


class wxMenuBar(wx.MenuBar):
    """ A wx.MenuBar subclass which exposes a convenient api.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxMenuBar.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wx.MenuBar.

        """
        super(wxMenuBar, self).__init__(*args, **kwargs)
        self._menus = []

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def OnMenuChanged(self, event):
        """ The event handler for the EVT_MENU_CHANGED event.

        This event handler will synchronize the menu changes with
        the menu bar.

        """
        if self.IsAttached():
            menu = event.GetEventObject()
            index = self._menus.index(menu)
            self.SetMenuLabel(index, menu.GetTitle())
            self.EnableTop(index, menu.IsEnabled())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def SetEnabled(self, enabled):
        """ Enables or disables the menu bar.

        """
        pass

    def AddMenu(self, menu):
        """ Add a wxMenu to the menu bar.

        If the menu already exists in the menu bar, this is a no-op.

        Parameters
        ----------
        menu : wxMenu
            The wxMenu instance to add to the menu bar.

        """
        menus = self._menus
        if menu not in menus:
            menus.append(menu)
            self.Append(menu, menu.GetTitle())
            menu.Bind(EVT_MENU_CHANGED, self.OnMenuChanged)

    def PostAttach(self):
        """ Update the state of the menu bar once it's been attached.

        """
        if self.IsAttached():
            for idx, item in enumerate(self._menus):
                if not item.IsEnabled():
                    self.EnableTop(idx, False)


class WxMenuBar(WxWidgetComponent):
    """ A Wx implementation of an Enaml MenuBar.

    """
    #: Storage for the menu ids
    _menu_ids = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying menu bar widget.

        """
        return wxMenuBar()

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(WxMenuBar, self).create(tree)
        self.set_menu_ids(tree['menu_ids'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(WxMenuBar, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for menu_id in self._menu_ids:
            child = find_child(menu_id)
            if child is not None:
                widget.AddMenu(child.widget())

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_menu_ids(self, menu_ids):
        """ Set the menu ids for the underlying control.

        """
        self._menu_ids = menu_ids

    def set_enabled(self, enabled):
        """ Overridden parent class method.

        This properly sets the enabled state on a menu bar.

        """
        self.widget().SetEnabled(enabled)

    def set_visible(self, visible):
        """ Overrdden parent class method.

        This properly sets the visible state on a menu bar.

        """
        pass

