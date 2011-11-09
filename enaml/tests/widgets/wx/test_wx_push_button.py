#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_test_assistant import WXTestAssistant, skip_nonwindows
from .. import push_button


@skip_nonwindows
class TestWxPushButton(WXTestAssistant, push_button.TestPushButton):
    """ WXPushButton tests. """

    def button_pressed(self):
        """ Press the button programmatically.

        """
        self.send_wx_event(self.widget, wx.EVT_LEFT_DOWN)

    def button_released(self):
        """ Release the button programmatically.

        """
        widget = self.widget
        self.send_wx_event(widget, wx.EVT_LEFT_UP)
        self.send_wx_event(widget, wx.EVT_LEAVE_WINDOW)

    def button_clicked(self):
        """ Click the button programmatically.

        """
        self.send_wx_event(self.widget, wx.EVT_BUTTON)

