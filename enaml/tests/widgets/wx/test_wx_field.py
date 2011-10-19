#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_test_assistant import WXTestAssistant
from .. import field


class TestWxField(WXTestAssistant, field.TestField):
    """ WXField tests. """

    def get_value(self, widget):
        """ Get the visible text of a field.

        """

        return widget.GetValue()

    def edit_text(self, widget, text):
        """ Simulate typing in a field.

        """
        widget.SetFocus()
        widget.WriteText(text)
        self.send_wx_event(widget, wx.EVT_TEXT)
        self.process_wx_events(self.app)

    def change_text(self, widget, text):
        """ Change text programmatically, rather than "edit" it.

        """
        widget.ChangeValue(text)
        self.send_wx_event(widget, wx.EVT_TEXT)
        self.process_wx_events(self.app)

    def set_cursor_position(self, widget, index):
        """ Set the cursor at a specific position.

        """
        widget.SetInsertionPoint(index)

    def get_cursor_position(self, widget):
        """ Get the cursor position.

        """
        return widget.GetInsertionPoint()

    def get_selected_text(self, widget):
        """ Get the currently-selected text from a field.

        """
        return widget.GetStringSelection()

    def press_return(self, widget):
        """ Simulate a press of the 'Return' key.

        """
        self.send_wx_event(widget, wx.EVT_TEXT_ENTER)
