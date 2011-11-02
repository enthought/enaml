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
    def create(self):
        """ Creates a wx.ComboBox.

        """
        self.widget = wx.ComboBox(self.parent_widget(), style=wx.CB_READONLY)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXComboBox, self).initialize()
        self.set_items()
        self.set_selection()

    def bind(self):
        """ Binds the event handlers for the combo box.

        """
        super(WXComboBox, self).bind()
        self.widget.Bind(wx.EVT_COMBOBOX, self.on_selected)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell__index_changed(self, index):
        """ The change handler for the '_index' attribute on the enaml
        shell.

        """
        shell = self.shell_obj
        self.set_selection()
        shell.selected = shell.value

    def shell_items_changed(self, items):
        """ The change handler for the 'items' attribute on the enaml
        shell.

        """
        old_selection = self.get_widget_selection()
        self.set_items()
        self.move_selection(old_selection)

    def shell_items_items_changed(self, items):
        """ The change handler for the 'items' event of the 'items'
        attribute on the enaml shell.

        """
        old_selection = self.get_widget_selection()
        self.set_items()
        self.move_selection(old_selection)

    def shell_to_string_changed(self, value):
        """ The change handler for the 'string' attribute on the enaml
        shell.

        """
        old_selection = self.get_widget_selection()
        self.set_items()
        self.move_selection(old_selection)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def on_selected(self, event):
        """ The event handler for a combo box selection event.

        """
        shell = self.shell_obj
        widget = self.widget
        index = widget.GetCurrentSelection()
        shell._index = index
        event.Skip()

    def set_items(self):
        """ Sets the items in the combo box.

        """
        shell = self.shell_obj
        widget = self.widget
        widget.SetItems(shell._labels)

    def set_selection(self):
        """ Set the selected value in the toolkit widget.

        """
        shell = self.shell_obj
        widget = self.widget
        widget.SetSelection(shell._index) # deselects if -1

    # FIXME: I found it easier to setup the selection move when the items
    # change in the widget side. The alternative will require that the
    # items attreibute in the abstract class is a Property of List(Any)
    # And I was a little worried to try it.
    def move_selection(self, value):
        """ Move the selection to the index where the value exists.

        The method attempts to find the index of the value. Moving
        the index does not cause a selected event to be fired. If the
        value is not found then the selection is undefined.

        """
        shell = self.shell_obj
        widget = self.widget
        index = widget.FindString(value)
        if index == wx.NOT_FOUND:
            shell._index = -1
        else:
            # we silently set the `_index` attribute since the selection
            # value has not changed
            shell.trait_setq(_index=index)
            self.set_selection()

    def get_widget_selection(self):
        """ Get the selected labels from the widget.

        """
        widget = self.widget
        return widget.GetStringSelection()
