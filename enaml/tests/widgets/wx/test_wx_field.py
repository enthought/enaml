#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from unittest import expectedFailure
import warnings

import wx

from .wx_test_assistant import WXTestAssistant, skip_nonwindows

from .. import field


warnings.simplefilter('ignore')


@skip_nonwindows
class TestWxField(WXTestAssistant, field.TestField):
    """ WXField tests. 

    """
    def get_value(self, widget):
        """ Get the visible text of a field.

        """
        self.process_wx_events(self.app)
        return widget.GetValue()

    def edit_text(self, widget, text):
        """ Simulate typing in a field.

        """
        widget.WriteText(text)
        self.send_wx_event(widget, wx.EVT_TEXT)
        self.process_wx_events(self.app)

    def change_text(self, widget, text):
        """ Change text programmatically, rather than "edit" it.

        """
        widget.ChangeValue(text)
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

    def gain_focus_if_needed(self, widget):
        """ Have the widget gain focus if required for the tests.

        """
        # wx doesn't seem to handle anything on the widget properly 
        # if the widget's not visible or doesn't have focus. So, in order 
        # for these tests to run, we need to gain focus on the widget. This
        # is not required in normal circumstances. Further, we can't get
        # widget to SetFocus before the value has been set, so we need
        # to "re-initialize" the widget it. This is really terrible and
        # it would be good to know which part of wx is broken so this
        # can be fixed.
        widget.SetFocus()
        val = self.component.value
        self.component.value = ''
        self.component.value = val

