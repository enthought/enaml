#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from traits.api import implements, cached_property, Property, Str, Event, List

from .wx_control import WXControl

from ..combo_box import IComboBoxImpl


class WXComboBox(WXControl):
    """ A wxPython implementation of ComboBox.

    Use a combo box to select a single item from a collection of items. 
    
    See Also
    --------
    ComboBox

    """
    implements(IComboBoxImpl)

    #---------------------------------------------------------------------------
    # IComboBoxImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates a wx.ComboBox.

        """
        self.widget = widget = wx.ComboBox(self.parent_widget(), 
                                           style=wx.CB_READONLY)
        widget.SetDoubleBuffered(True)

    def initialize_widget(self):
        """ Intializes the widget with the attributes of this instance.

        """
        self.set_items(self.str_items)
        self.set_value(self.str_value)
        self.bind()

    def parent_items_changed(self, items):
        """ The change handler for the 'items' attribute on the parent.

        """
        self.refresh_items = True
    
    def parent_items_items_changed(self, items):
        """ The change handler for the 'items' event of the 'items'
        attribute on the parent.

        """
        self.refresh_items = True
    
    def parent_value_changed(self, value):
        """ The change handler for the 'value' attribute on the parent.

        """
        self.refresh_value = True

    def parent_to_string_changed(self, value):
        """ The change handler for the 'string' attribute on the parent.

        """
        self.refresh_items = True
        self.refresh_value = True
    
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    refresh_items = Event

    refresh_value = Event

    str_items = Property(List(Str), depends_on='refresh_items')

    str_value = Property(Str, depends_on='refresh_value')

    items_set = Property(depends_on='refresh_items')

    @cached_property
    def _get_str_items(self):
        """ The cached property getter for 'str_items'.
        
        """ 
        parent = self.parent
        return map(parent.to_string, parent.items)
    
    @cached_property
    def _get_str_value(self):
        """ The cached property getter for 'str_value'.

        """
        parent = self.parent
        return parent.to_string(parent.value)
    
    @cached_property
    def _get_items_set(self):
        """ The cached property getter for 'items_set'.

        """
        return set(self.parent.items)

    def _str_items_changed(self, str_items):
        """ The change handler for 'str_items'.

        """
        self.set_items(str_items)
    
    def _str_value_changed(self, str_value):
        """ The change handler for 'str_value'.

        """
        self.set_value(str_value)

    def bind(self):
        """ Binds the event handlers for the combo box.

        """
        self.widget.Bind(wx.EVT_COMBOBOX, self.on_selected)

    def on_selected(self, event):
        """ The event handler for a combo box selection event.

        """
        parent = self.parent
        idx = self.widget.GetCurrentSelection()
        value = parent.items[idx]
        parent.value = value
        parent.selected = value
        event.Skip()

    def set_items(self, str_items):
        """ Sets the items in the combo box.

        """
        self.widget.SetItems(str_items)

    def set_value(self, str_value):
        """ Sets the value in the combo box, or resets the combo box
        if the value is not in the list of items.

        """
        value = self.parent.value
        if value not in self.items_set:
            # This forces a deselection albeit through expensive means
            # for large combo boxes. But, there is no deselect method '
            # on the wx.ComboBox. Hooray wx!
            self.widget.SetItems(self.widget.GetItems())
        else:
            self.widget.SetValue(str_value)

