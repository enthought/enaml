#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_toggle_control import WXToggleControl

from ..check_box import AbstractTkCheckBox


class WXCheckBox(WXToggleControl, AbstractTkCheckBox):
    """ A wxPython implementation of CheckBox.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.CheckBox.

        """
        self.widget = wx.CheckBox(parent)

    def bind(self):
        """ Binds the event handlers for the check box.

        """
        super(WXCheckBox, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_CHECKBOX, self.on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self.on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self.on_released)

