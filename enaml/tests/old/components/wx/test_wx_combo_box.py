#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_test_assistant import WXTestAssistant, skip_nonwindows

from .. import combo_box


@skip_nonwindows
class TestWXComboBox(WXTestAssistant, combo_box.TestComboBox):
    """ WXComboBox tests. 

    """
    def get_selected_text(self, widget):
        """ Get the current selected text of a combo box.

        """
        return widget.GetStringSelection()

    def get_item_text(self, widget, index):
        """ Get the text of a combo box item at a particular index.

        """
        return widget.GetString(index)

    def select_item(self, widget, index):
        """ Fire an event to simulate the selection of an item.

        """
        widget.SetSelection(index)
        self.send_wx_event(widget, wx.EVT_COMBOBOX)

