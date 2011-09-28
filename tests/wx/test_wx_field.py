#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from . import send_wx_event, process_wx_events

from ..common import field
from enaml.toolkit import wx_toolkit


class TestWxField(field.TestField):
    """ WXField tests. """

    toolkit = wx_toolkit()

    def get_value(self, widget):
        """ Get the visible text of a field.

        """
        
        return widget.GetValue()

    def edit_text(self, widget, text):
        """ Simulate typing in a field.

        """
        widget.SetFocus()
        widget.WriteText(text)
        send_wx_event(widget, wx.EVT_TEXT)
        process_wx_events(self.view.toolkit.app)
    
    def change_text(self, widget, text):
        """ Change text programmatically, rather than "edit" it.
        
        """
        widget.ChangeValue(text)
        send_wx_event(widget, wx.EVT_TEXT)
        process_wx_events(self.view.toolkit.app)

    def set_cursor(self, widget, index):
        """ Set the cursor at a specific position.
        
        """
        widget.SetInsertionPoint(index)
        
    def get_cursor(self, widget):
        """ Get the cursor position.
        
        """
        return widget.GetInsertionPoint()

    def set_selected_text(self, widget, start, stop):
        """ Select text in a field.
        
        """
        widget.SetSelection(start, stop)

    def get_selected_text(self, widget):
        """ Get the currently-selected text from a field.
        
        """
        return widget.GetStringSelection()

    def press_return(self, widget):
        """ Simulate a press of the 'Return' key.
        
        """
        send_wx_event(widget, wx.EVT_TEXT_ENTER)
