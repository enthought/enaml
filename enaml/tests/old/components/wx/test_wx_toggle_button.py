#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_test_assistant import WXTestAssistant, skip_nonwindows

from .. import toggle_button

@skip_nonwindows
class TestWXToggleButton(WXTestAssistant, toggle_button.TestToggleButton):
    """ WXToggleButton tests. 
    
    """
    def get_text(self, widget):
        """ Returns the text from the tookit widget.

        """
        return widget.GetLabel()

    def get_checked(self, widget):
        """ Returns the checked status from the tookit widget.

        """
        return widget.GetValue()

    def toggle_button_pressed(self, widget):
        """ Press the toggle button programmatically.

        """
        self.send_wx_event(widget, wx.EVT_LEFT_DOWN)

    def toggle_button_released(self, widget):
        """ Release the button programmatically.

        """
        self.send_wx_event(widget, wx.EVT_LEFT_UP)
        self.send_wx_event(widget, wx.EVT_LEAVE_WINDOW)

    def toggle_button_toggle(self, widget):
        """ Toggle the button programmatically.

        """
        self.send_wx_event(widget, wx.EVT_TOGGLEBUTTON)

