#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl

from ..combo_box import AbstractTkComboBox


class WXComboBox(WXControl, AbstractTkComboBox):
    """ A wxPython implementation of ComboBox.

    Use a combo box to select a single item from a collection of items.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates a wx.ComboBox.

        """
        self.widget = wx.ComboBox(parent, style=wx.CB_READONLY)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXComboBox, self).initialize()
        shell = self.shell_obj
        self.set_items(shell.labels)
        self.set_selection(shell.index)

    def bind(self):
        """ Binds the event handlers for the combo box.

        """
        super(WXComboBox, self).bind()
        self.widget.Bind(wx.EVT_COMBOBOX, self.on_selected)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_index_changed(self, index):
        """ The change handler for the '_index' attribute on the enaml
        shell.

        """
        self.set_selection(index)

    def shell_labels_changed(self, labels):
        """ The change handler for the 'labels' attribute on the shell
        object.

        """
        self.set_items(labels)

    def on_selected(self, event):
        """ The event handler for a combo box selection event.

        """
        shell = self.shell_obj
        curr_index = self.widget.GetCurrentSelection()
        shell.index = curr_index

        # Only fire the selected event if we have a valid selection
        if curr_index != -1:
            shell.selected(shell.value)

        event.Skip()

    def set_items(self, str_items):
        """ Sets the items in the combo box.

        """
        # wx does not emit events on SetItems or SetSelection, so we
        # do not need any feedback guards here.
        self.widget.SetItems(str_items)
        self.widget.SetSelection(self.shell_obj.index)

    def set_selection(self, index):
        """ Set the selected value in the toolkit widget.

        """
        # wx does not emit events on SetSelection, so we do 
        # not need any feedback guards here.
        self.widget.SetSelection(index) # deselects if -1

