#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_toggle_control import WXToggleControl
from ..check_box import AbstractTkCheckBox

class WXCheckBox(WXToggleControl, AbstractTkCheckBox):
    """ A wxPython implementation of CheckBox.

    A Checkbox provides a toggleable control using a wx.CheckBox.

    """

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates and the wx.CheckBox.

        """
        self.widget = widget = wx.CheckBox(self.parent_widget())
        widget.SetDoubleBuffered(True)

    def bind(self):
        """ Binds the event handlers for the check box. Not meant for
        public consumption.

        """
        super(WXCheckBox, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_CHECKBOX, self.on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self.on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self.on_released)

