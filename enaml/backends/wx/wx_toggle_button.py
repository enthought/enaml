#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_toggle_control import WXToggleControl

from ...components.toggle_button import AbstractTkToggleButton


class WXToggleButton(WXToggleControl, AbstractTkToggleButton):
    """ A wxPython implementation of ToggleButton.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.ToggleButton.

        """
        self.widget = wx.ToggleButton(parent)

    def bind(self):
        """ Binds the event handlers for the check box.

        """
        super(WXToggleButton, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self.on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self.on_released)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_icon_changed(self, icon):
        """ The change handler for the 'icon' attribute.

        This is currently not implemented because the standard 
        wx.ToggleButton does not support images.

        """
        pass

    def shell_icon_size_changed(self, icon_size):
        """ The change handler for the 'icon_size' attribute.

        This is currently not implemented because the standard 
        wx.ToggleButton does not support images.

        """
        pass

