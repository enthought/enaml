#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_widget_component import WXWidgetComponent

from ...components.window import AbstractTkWindow


class WXWindow(WXWidgetComponent, AbstractTkWindow):
    """ A wxPython implementation of a Window.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying Wx widget.

        """
        self.widget = wx.Frame(parent)

    def initialize(self):
        """ Intializes the attributes on the wx.Frame.

        """
        super(WXWindow, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.set_icon(shell.icon)
        self.set_central_widget(shell.central_widget)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def maximize(self):
        """ Maximizes the window to fill the screen.

        """
        self.widget.Maximize(True)
            
    def minimize(self):
        """ Minimizes the window to the task bar.

        """
        self.widget.Iconize(True)
            
    def restore(self):
        """ Restores the window after it has been minimized or maximized.

        """
        self.widget.Maximize(False)

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute on the shell
        object.

        """
        self.set_title(title)

    def shell_icon_changed(self, icon):
        """ The change handler for the 'icon' attribute on the shell
        object.

        """
        self.set_icon(icon)

    def shell_central_widget_changed(self, central_widget):
        """ The change handler for the 'central_widget' attribute on 
        the shell object.

        """
        self.set_central_widget(central_widget)
       
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_central_widget(self, central_widget):
        """ Sets the central widget in the window with the given value.

        """
        # We shouldn't need to do anything here since the new widget
        # will already have been parented properly by the Include and
        # a relayout will have been requested.
        pass

    def set_icon(self, icon):
        """ Sets the icon of the window.

        """
        wxicon = self.widget.GetIcon()
        if icon is not None:
            img = icon.get_image((32, 32), mode='normal')
            bmp = img.as_wxBitmap()
            wxicon.CopyFromBitmap(bmp)
        self.widget.SetIcon(wxicon)

    def set_title(self, title):
        """ Sets the title of the frame.

        """
        self.widget.SetTitle(title)

