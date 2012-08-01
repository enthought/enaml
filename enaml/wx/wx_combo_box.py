#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_constraints_widget import WxConstraintsWidget


class WxComboBox(WxConstraintsWidget):
    """ A Wx implementation of an Enaml ComboBox.
    
    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = wx.ComboBox(self.parent_widget, style=wx.CB_READONLY)

    def initialize(self, attrs):
        """ Initialize the widget's attributes

        """
        super(WxComboBox, self).initialize(attrs)
        self.set_items(attrs['items'])
        self.set_index(attrs['index'])
        self.widget.Bind(wx.EVT_COMBOBOX, self.on_index_changed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_index(self, content):
        """ Handle the 'set_index' action from the Enaml widget.

        """
        self.set_index(content['index'])

    def on_action_set_items(self, content):
        """ Handle the 'set_items' action from the Enaml widget.

        """
        self.set_items(content['items'])

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_index_changed(self, event):
        """ The signal handler for the index changed signal.

        """
        content = {'index': self.widget.GetCurrentSelection()}
        self.send_action('index_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_items(self, items):
        """ Set the items of the ComboBox.

        """
        sel = self.widget.GetCurrentSelection()
        self.widget.SetItems(items)
        self.widget.SetSelection(sel)

    def set_index(self, index):
        """ Set the current index of the ComboBox

        """
        self.widget.SetSelection(index)

