#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

import wx

from .wx_component import WXComponent
from .wx_menu import wxEnamlMenu

from ..menu_bar import AbstractTkMenuBar


class wxEnamlMenuBar(wx.MenuBar):
    """ A wx.MenuBar subclass which adapts the wx menu bar api to work 
    with the menu semantics of Enaml.

    """
    def __init__(self, parent, *args, **kwargs):
        """ Initialize a wxEnamlMenuBar.

        Parameters
        ----------
        parent : wx.Frame
            An instance of wx.Frame to which this menu bar is attached.

        *args
            Additional positional arguments to pass to the wx.MenuBar
            constructor.
        
        **kwargs
            Additional keyword arguments to pass to the wx.MenuBar
            constructor.

        """
        if not isinstance(parent, wx.Frame):
            msg = ('The parent of a wxCustomMenuBar must be an instance of '
                   'wx.Frame. Got %s instead' % parent)
            raise TypeError(msg)
        super(wxEnamlMenuBar, self).__init__(*args, **kwargs)
        self._parent = weakref.ref(parent)
        self._enabled = True

    def GetParent(self):
        """ Returns the parent of this menu bar, which will be a wxFrame,
        or None if the frame has already been garbage collected.

        """
        return self._parent()

    def Append(self, menu, title=''):
        """ Appends the given menu to the menu bar with the given title.

        Parameters
        ----------
        menu : wxEnamlMenu
            The instance of wxEnamlMenu which should be appended to the
            menu bar.
        
        title : string, optional
            The title that should be used for the menu. If not provided
            or an empty string, a unique mangled title will be created.

        """
        idx = self.GetMenuCount()
        self.Insert(idx, menu, title)

    def Insert(self, idx, menu, title=''):
        """ Appends the given menu to the menu bar with the given title.

        Parameters
        ----------
        idx : int
            The index at which to insert the menu.

        menu : wxEnamlMenu
            The instance of wxEnamlMenu which should be appended to the
            menu bar.
        
        title : string, optional
            The title that should be used for the menu. If not provided
            or an empty string, a unique mangled title will be created.

        """
        if idx < 0 or idx > self.GetMenuCount():
            msg = 'Cannot insert menu. Index %s is out of range.'
            raise ValueError(msg % idx)

        if not isinstance(menu, wxEnamlMenu):
            msg = ('Can only insert instances of wxEnamlMenu to a '
                   'wxEnamlMenuBar. Got %s instead.')
            raise TypeError(msg % menu)

        # wx will raise a C++ exception if the title is an empty string.
        # In such cases, we mangle a unique title for the menu.
        if not title:
            title = 'Menu_' + self.GetMenuCount()
        
        super(wxEnamlMenuBar, self).Insert(idx, menu, title)
        
        # After adding the menu, we need to check whether we should
        # disable the menu based on its enabled state. This api is
        # a bit weird since wx forces us to set the enabledness of
        # the menu through the menubar object, so the repsonsibility
        # of that is shared between here and the Menu object itself.
        if not self.IsEnabled() or not menu.IsEnabled():
            self.EnableTop(self.GetMenuCount() - 1, False)

    def RemoveAll(self):
        """ Removes all the menus from the menu bar. The menus are not
        destroyed.

        """
        while self.GetMenuCount():
            self.Remove(0)
        
    def IsEnabled(self):
        """ Returns whether or not the menu bar is enabled. Note that 
        this overrides a parent class method of the same name but with
        a different call signature and different semantics.

        """
        return self._enabled

    def Enable(self, enable):
        """ Enables or disables all of the underlying children. Note 
        that this overrides a parent class method of the same name 
        but with a different call signature and different semantics.

        """
        menus = [item[0] for item in self.GetMenus()]
        for idx, menu in enumerate(menus):
            if enable:
                # Only enable the menu if its underlying enabled state
                # is True. This cooperation is required because of the
                # funky menu api of wx. The menu itself also has logic
                # which will toggle its enabled state.
                if menu.IsEnabled():
                    self.EnableTop(idx, True)
            else:
                self.EnableTop(idx, False)
        self._enabled = enable

    def Destroy(self):
        """ An overridden destructor method which removes itself from
        the parent before invoking the actual destructor.

        """
        if self:
            parent = self._parent()
            if parent is not None:
                if parent.GetMenuBar() == self:
                    parent.SetMenuBar(None)
            super(wxEnamlMenuBar, self).Destroy()


class WXMenuBar(WXComponent, AbstractTkMenuBar):
    """ A Wx implementation of a MenuBar.

    """
    def create(self, parent):
        """ Creates the underlying wxMenuBar.

        """
        self.widget = wxEnamlMenuBar(parent)

    def initialize(self):
        """ Initializes the wxMenuBar.

        """
        super(WXMenuBar, self).initialize()
        self.update_menus()
    
    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def shell_menus_changed(self):
        """ The change handler for the 'menus' attribute on the shell
        object.

        """
        self.update_menus()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def update_menus(self):
        """ Updates the menu bar with the child menu objects.

        """
        # We can't reason reliably on the proper ordering of menus
        # in the menu bar because of the variety of possible uses
        # of the Include component. Instead, we just remove the 
        # existing menus, and then add the desired menus.
        widget = self.widget
        widget.RemoveAll()
        for menu in self.shell_obj.menus:
            widget.Append(menu.toolkit_widget, menu.title)

