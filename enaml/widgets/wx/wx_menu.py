#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

import wx

from .wx_action import wxEnamlAction
from .wx_component import WXComponent

from ..menu import AbstractTkMenu


# A note to future developers who consider trying to code the event 
# handling logic to implement the about_to_show/hide functionality:
# Don't. I wasted 8 hours of my life trying to get it to work, only
# to have wx get in my way at every step. For example, in order to 
# actually receive EVT_MENU_OPEN/CLOSE events on Windows, one has to 
# bind to the events on the parent wxFrame rather than the menus 
# themselves. Ok fine. You can do that, only to have the wxMenuEvent 
# return None from GetMenu() at various times. For example, it will 
# always give None from an EVT_MENU_CLOSE, and it will give None from 
# an EVT_MENU_OPEN on a submenu. This makes it utterly pointless to 
# try to do any handling since one has no idea which menu actually 
# triggered the event. So until wx actually fixes the menu events 
# (don't hold your breath, the issue has been known since 2006), any
# effort to get it to work won't be worth it. Just use Qt.
class wxEnamlMenu(wx.Menu):
    """ A wx.Menu subclass which adapts the wx menu api to work with the
    menu semantics of Enaml.

    """
    def __init__(self, parent, *args, **kwargs):
        """ Initialize a wxEnamlMenu.

        Parameters
        ----------
        parent : wxEnamlMenuBar or wxEnamlMenu
            The logic parent of this menu.

        *args
            Additional positional arguments to pass to the wx.MenuBar
            constructor.
        
        **kwargs
            Additional keyword arguments to pass to the wx.MenuBar
            constructor.
        
        """
        super(wxEnamlMenu, self).__init__(*args, **kwargs)
        self._parent = weakref.ref(parent)
        self._enabled = True

    def GetParent(self):
        """ Returns the parent of this menu.

        """
        return self._parent()

    def RemoveAll(self):
        """ Removes all of the menu items from the menu. It does not 
        destroy any of the menu items.

        """
        items = list(self.GetMenuItems())
        for item in items:
            self.RemoveItem(item)

    def IsEnabled(self):
        """ Returns whether or not the menu is enabled. Note that this
        overrides a parent class method of the same name but with a 
        different call signature and different semantics.

        """
        return self._enabled

    def Enable(self, enable):
        """ Enables or disables the menu. Note that this overrides a 
        parent class method of the same name but with a different call 
        signature and different semantics.

        """
        parent = self._parent()
        if parent is not None and parent.IsEnabled():
            if isinstance(parent, wx.MenuBar):
                for idx, (menu, _) in enumerate(parent.GetMenus()):
                    if menu == self:
                        parent.EnableTop(idx, enable)
                        break
            elif isinstance(parent, wx.Menu):
                for item in parent.GetMenuItems():
                    if item.GetSubMenu() == self:
                        item.Enable(enable)
                        break
            else:
                msg = 'Invalid parent for wxEnamlMenu %s'
                raise TypeError(msg % parent)
        self._enabled = enable

    def SetTitle(self, title):
        """ Sets the title for the menu. Note that this overrides a 
        parent class method of the same name but with a different call 
        signature and different semantics.

        """
        # We do *not* want to use the default SetTitle implementation 
        # here since it doesn't change the title of the entry in the 
        # menubar. Instead, it adds a non-functional bold-faced entry 
        # into the menu itself, followed by a separator and the rest 
        # of the menu items. The docs say its meant for popup menus,
        # but I find it just confuses the api and serves no purpose.
        parent = self._parent()
        if parent is not None:
            if isinstance(parent, wx.MenuBar):
                for idx, (menu, _) in enumerate(parent.GetMenus()):
                    if menu == self:
                        parent.SetMenuLabel(idx, title)
                        break
            elif isinstance(parent, wx.Menu):
                for item in parent.GetMenuItems():
                    if item.GetSubMenu() == self:
                        item.SetItemLabel(title)
                        break
            else:
                msg = 'Invalid parent for wxEnamlMenu %s'
                raise TypeError(msg % parent)

    def Destroy(self):
        """ An overridden parent class method which removes this menu
        from its parent before invoking the actual destructor.

        """
        if self:
            parent = self._parent()
            if parent is not None:
                if isinstance(parent, wx.MenuBar):
                    for idx, (menu, _) in enumerate(parent.GetMenus()):
                        if menu == self:
                            parent.Remove(idx)
                            break
                elif isinstance(parent, wx.Menu):
                    for item in parent.GetMenuItems():
                        if item.GetSubMenu() == self:
                            parent.RemoveItem(item)
                            break
                else:
                    msg = 'Invalid parent for wxEnamlMenu %s'
                    raise TypeError(msg % parent)
            super(wxEnamlMenu, self).Destroy()


class WXMenu(WXComponent, AbstractTkMenu):
    """ A Wx implementation of Menu.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QMenu object.

        """
        self.widget = wxEnamlMenu(parent)

    def initialize(self):
        """ Initialize the underlying QMenu object.

        """
        super(WXMenu, self).initialize()
        # We don't need to initialize the title for a wx Menu since 
        # that is handled by its parent when its added to the menubar
        # or menu. However, if the title changes, it is updated by 
        # the change handler defined below.
        self.set_title(self.shell_obj.title)
        self.update_contents()
    
    # There is nothing to bind on a Menu since the wx Menu doesn't
    # support proper show/hide notification. See the block comment
    # above the definition of wxEnamlMenu for more explanation.

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def shell_title_changed(self, text):
        """ The change handler for the 'title' attribute on the shell
        object.

        """
        self.set_title(text)
        
    def shell_contents_changed(self, contents):
        """ The change handler for the 'contents' attribute on the shell
        object. 

        """
        self.update_contents()

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_about_to_show(self, event):
        """ A signal handler for the 'aboutToShow' signal of the QMenu.

        """
        self.shell_obj.about_to_show()

    def on_about_to_hide(self, event):
        """ A signal handler for the 'aboutToHide' signal of the QMenu.

        """
        self.shell_obj.about_to_hide()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def update_contents(self):
        """ Updates the contents of the Menu.

        """
        # We can't reason reliably on the proper ordering of menus
        # in the menu bar because of the variety of possible uses
        # of the Include component. Instead, we just remove the 
        # existing menu items, and then add the new ones.
        widget = self.widget
        widget.RemoveAll()
        for item in self.shell_obj.contents:
            child_widget = item.toolkit_widget
            if isinstance(child_widget, wxEnamlMenu):
                widget.AppendSubMenu(child_widget, item.title)
            elif isinstance(child_widget, wxEnamlAction):
                child_widget.Install()
            else:
                msg = 'Invalid child for wxEnamlMenu: %s'
                raise TypeError(msg % child_widget)

    def set_title(self, title):
        """ Sets the title of the wxMenu object.

        """
        self.widget.SetTitle(title)
        
    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def popup(self, blocking=True):
        """ Pops up the menu on the toplevel widget using the current 
        position of the cursor. The blocking flag is ignored since it
        is not supported by wx. All popup menus block on wx.

        """
        top_component = self.shell_obj.toplevel_component()
        try:
            toplevel_window = top_component.toolkit_widget
        except AttributeError:
            windows = wx.GetTopLevelWindows()
            if len(windows) == 0:
                msg = 'Cannot find a suitable toplevel window for popup menu'
                raise ValueError(msg)
            toplevel_window = windows[0]
        toplevel_window.PopupMenu(self.widget)

