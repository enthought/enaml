#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_component import WXComponent

from ..menu_bar import AbstractTkMenuBar


class WXMenuBar(WXComponent, AbstractTkMenuBar):
    """ A Wx implementation of a MenuBar.

    """
    def create(self, parent):
        """ Creates the underlying wxMenuBar.

        """
        self.widget = wx.MenuBar()

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
        count = widget.GetMenuCount()
        
        while count != 0:
            count -= 1
            widget.Remove(count)

        for menu in self.shell_obj.menus:
            widget.Append(menu.toolkit_widget, 'what')
              
    def set_bg_color(self, color):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenuBar.

        """
        pass
    
    def set_fg_color(self, color):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenuBar.

        """
        pass
    
    def set_font(self, font):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QMenuBar.

        """
        pass

    def set_enabled(self, enabled):
        pass

