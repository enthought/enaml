#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from . import process_wx_events

from ..common import field
from enaml.toolkit import wx_toolkit


class TestWxField(field.TestField):
    """ WXField tests. """

    toolkit = wx_toolkit()

    def get_value(self, widget):
        """ Get the visible text of a field.

        """
        process_wx_events(self.view.toolkit.app)
        return widget.GetValue()

    def send_text(self, widget, text):
        """ Simulate typing in a field.

        """
        widget.SetFocus()
        widget.WriteText(text)
        
    def clear_text_and_focus(self, widget):
        """ Clear the field's text, and remove its focus.
        
        """
        widget.Clear()
        event = wx.PyCommandEvent(wx.EVT_KILL_FOCUS.typeId, widget.GetId())
        widget.GetEventHandler().ProcessEvent(event)
