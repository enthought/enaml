#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_test_assistant import WXTestAssistant, skip_nonwindows
from .. import check_box

@skip_nonwindows
class TestWXCheckBox(WXTestAssistant, check_box.TestCheckBox):
    """ WXCheckbox tests. """

    def get_text(self, widget):
        """ Returns the text from the tookit widget.

        """
        return widget.GetLabel()

    def get_checked(self, widget):
        """ Returns the checked status from the tookit widget.

        """
        return widget.GetValue()

    def checkbox_pressed(self, widget):
        """ Press the checkbox programmatically.

        """
        self.send_wx_event(widget, wx.EVT_LEFT_DOWN)

    def checkbox_released(self, widget):
        """ Release the button programmatically.

        """
        self.send_wx_event(widget, wx.EVT_LEFT_UP)
        self.send_wx_event(widget, wx.EVT_LEAVE_WINDOW)

    def checkbox_toggle(self, widget):
        """ Toggle the button programmatically.

        """
        self.send_wx_event(widget, wx.EVT_CHECKBOX)
