#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_component import WXComponent

from ..menu import AbstractTkMenu


class WXMenu(WXComponent, AbstractTkMenu):
    """ A Wx implementation of Menu.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QMenu object.

        """
        self.widget = wx.Menu()
        
        # A private dict of menu items generated while populating the 
        # menu. We need to keep this state around so that we can remove
        # items from the menu as needed.
        self._menu_items = {}

    def initialize(self):
        """ Initialize the underlying QMenu object.

        """
        super(WXMenu, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.update_contents()
    
    def bind(self):
        """ Binds the event handlers for the underlying QMenu object.

        """
        super(WXMenu, self).bind()
        #widget = self.widget
        #widget.aboutToShow.connect(self.on_about_to_show)
        #widget.aboutToHide.connect(self.on_about_to_hide)

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
    def on_about_to_show(self):
        """ A signal handler for the 'aboutToShow' signal of the QMenu.

        """
        self.shell_obj.about_to_show = True

    def on_about_to_hide(self):
        """ A signal handler for the 'aboutToHide' signal of the QMenu.

        """
        self.shell_obj.about_to_hide = True

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def update_contents(self):
        """ Updates the contents of the Menu.

        """
        # We can't reason reliably on the proper ordering of menus
        # in the menu bar because of the variety of possible uses
        # of the Include component. Instead, we just remove the 
        # existing menus, and then add the desired menus.
        widget = self.widget
        menu_items = self._menu_items
        for item in menu_items.itervalues():
            widget.RemoveItem(item)
        menu_items.clear()

        for item in self.shell_obj.contents:
            child_widget = item.toolkit_widget
            if isinstance(child_widget, wx.Menu):
                mi = widget.AddSubMenu(child_widget, child_widget.GetTitle())
                menu_items[child_widget] = mi

    def set_title(self, title):
        """ Sets the title of the QMenu object.

        """
        self.widget.SetTitle(title)

    def set_bg_color(self, color):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenu.

        """
        pass
    
    def set_fg_color(self, color):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenu.

        """
        pass
    
    def set_font(self, font):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenu.

        """
        pass

    def set_enabled(self, enabled):
        pass
        
    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def popup(self, pos=None, blocking=True):
        """ Pops up the menu at the appropriate position using a blocking
        context if requested.

        """
        # if pos is None:
        #     pos = QtGui.QCursor.pos()
        # else:
        #     pos = QtCore.QPoint(*pos)

        # if blocking:
        #     self.widget.exec_(pos)
        # else:
        #     self.widget.popup(pos)

