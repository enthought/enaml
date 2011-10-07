#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from . import send_wx_event

from .. import push_button
from enaml.toolkit import wx_toolkit


class TestWxPushButton(push_button.TestPushButton):
    """ WXPushButton tests. """

    toolkit = wx_toolkit()

    def button_pressed(self):
        """ Press the button programmatically.

        """
        send_wx_event(self.widget, wx.EVT_LEFT_DOWN)

    def button_released(self):
        """ Release the button programmatically.

        """
        widget = self.widget
        send_wx_event(widget, wx.EVT_LEFT_UP)
        send_wx_event(widget, wx.EVT_LEAVE_WINDOW)

    def button_clicked(self):
        """ Click the button programmatically.

        """
        send_wx_event(self.widget, wx.EVT_BUTTON)

