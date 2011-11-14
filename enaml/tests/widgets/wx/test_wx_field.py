#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
from unittest import expectedFailure
from .wx_test_assistant import WXTestAssistant, skip_nonwindows
from .. import field


@skip_nonwindows
class TestWxField(WXTestAssistant, field.TestField):
    """ WXField tests. """

    def get_value(self, widget):
        """ Get the visible text of a field.

        """
        self.process_wx_events(self.app)
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
        self.process_wx_events(self.app)

    def get_cursor_position(self, widget):
        """ Get the cursor position.

        """
        self.process_wx_events(self.app)
        return widget.GetInsertionPoint()

    def get_password_mode(self, widget):
        """ Get the password mode status of the widget.

        Currently WXField only supports `password` and normal`.

        """
        # FIXME: specifically checking if we are using WX and the component
        # is set to 'silent' so that we can set the test to expected failure
        # we use this ugly hack.
        @expectedFailure
        def silent_password_mode(self):
            self.fail('Currently WXField only supports `password` and normal`.')

        component = self.component
        if component.password_mode == 'silent':
            silent_password_mode()

        self.process_wx_events(self.app)
        if widget.HasFlag(wx.TE_PASSWORD):
            return 'password'
        else:
            return 'normal'

    def get_selected_text(self, widget):
        """ Get the currently-selected text from a field.

        """
        self.process_wx_events(self.app)
        return widget.GetStringSelection()

    def press_return(self, widget):
        """ Simulate a press of the 'Return' key.

        """
        self.send_wx_event(widget, wx.EVT_TEXT_ENTER)
        self.process_wx_events(self.app)

