#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_window import WXWindow

from ..main_window import AbstractTkMainWindow


class  WXMainWindow(WXWindow, AbstractTkMainWindow):
    """ A Wx implementation of a MainWindow.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wxFrame object.

        """
        self.widget = wx.Frame(parent)
    
    def initialize(self):
        """ Intializes the attributes on the wx.Frame.

        """
        super(WXMainWindow, self).initialize()
        self.update_menu_bar()

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def shell_menu_bar_changed(self, menu_bar):
        """ Update the menu bar of the window with the new value from
        the shell object.

        """
        self.update_menu_bar()

    #--------------------------------------------------------------------------
    # Abstract Implementation
    #--------------------------------------------------------------------------
    def menu_bar_height(self):
        """ Returns the height of the menu bar in pixels. If the menu
        bar does not have an effect on the height of the main window,
        this method returns Zero.

        """
        menu_bar = self.widget.GetMenuBar()
        if menu_bar is None:
            res = 0
        else:
            # XXX can we do better than this?
            if wx.Platform == '__WXMAC__':
                res = 0
            else:
                res = 21
        return res

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def update_menu_bar(self):
        """ Updates the menu bar in the main window with the value
        from the shell object.

        """
        menu_bar = self.shell_obj.menu_bar
        if menu_bar is not None:
            self.widget.SetMenuBar(menu_bar.toolkit_widget)
        else:
            self.widget.SetMenuBar(None)

    def update_central_widget(self):
        """ Updates the central widget in the main window with the 
        value from the shell object.

        """
        # We shouldn't need to do anything here since the new widget
        # will already have been parented properly by the Include and
        # a relayout will have been requested.
        pass

    def set_visible(self, visible):
        """ Overridden from the parent class to raise the window to
        the front if it should be shown.

        """
        widget = self.widget
        if visible:
            widget.Show(True)
            widget.Raise()
        else:
            widget.Show(False)

