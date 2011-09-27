#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from . import send_wx_event
from ..common import check_box
from enaml.toolkit import wx_toolkit

class TestWXCheckBox(check_box.TestCheckBox):
    """ WXCheckbox tests. """

    toolkit = wx_toolkit()

    def get_text(self, widget):
        """ Returns the text from the tookit widget.

        """
        return widget.GetLabel()

    def checked_status(self, widget):
        """ Returns the text from the tookit widget.


        """
        return widget.GetValue()

    def checkbox_pressed(self, widget):
        """ Press the checkbox programmatically.

        """
        send_wx_event(widget, wx.EVT_LEFT_DOWN)

    def checkbox_released(self, widget):
        """ Release the button programmatically.

        """
        send_wx_event(widget, wx.EVT_LEFT_UP)
        send_wx_event(widget, wx.EVT_LEAVE_WINDOW)

    def checkbox_toggle(self, widget):
        """ Toggle the button programmatically.

        """
        send_wx_event(widget, wx.EVT_CHECKBOX)
