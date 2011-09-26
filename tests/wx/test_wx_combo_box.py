#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from . import send_wx_event

from ..common import combo_box
from enaml.toolkit import wx_toolkit


class TestWxComboBox(combo_box.TestComboBox):
    """ WXComboBox tests. """

    toolkit = wx_toolkit()

    def get_selected_text(self, widget):
        """ Get the current selected text of a combo box.

        """
        return widget.GetValue()

    def get_item_text(self, widget, index):
        """ Get the text of a combo box item at a particular index.

        """
        return widget.GetString(index)

    def select_item(self, widget, index):
        """ Fire an event to simulate the selection of an item.
        
        """
        widget.SetSelection(index)
        send_wx_event(widget, wx.EVT_COMBOBOX)
