import wx

from traits.api import (implements, List, Any, Callable, Event, Property, 
                        cached_property, on_trait_change)

from .wx_element import WXElement

from ..i_combo_box import IComboBox


class WXComboBox(WXElement):
    """ A wxPython implementation of IComboBox.

    Use a combo box to select a single item from a collection of
    items. To select multiple items from a collection of items
    use a List widget.
    
    See Also
    --------
    IComboBox

    """
    implements(IComboBox)

    #===========================================================================
    # IComboBox interface
    #===========================================================================
    items = List(Any)

    value = Any

    to_string = Callable(str)

    selected = Event

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates and binds a wx.ComboBox.

        This is called by the 'layout' method and is not meant for public
        consumption.

        """
        widget = wx.ComboBox(self.parent_widget(), style=wx.CB_READONLY)
        widget.Bind(wx.EVT_COMBOBOX, self._on_selected)
        self.widget = widget

    def init_attributes(self):
        """ Intializes the widget with the attributes of this instance.
        
        This is called by the 'layout' method and is not meant for public
        consumption.

        """
        self.set_items()
        self.set_value()

    def init_meta_handlers(self):
        """ Intializes the meta handlers for this control.
        
        This is called by the 'layout' method and is not meant for public
        consumption.
        
        """
        pass

    #---------------------------------------------------------------------------
    # Properties
    #---------------------------------------------------------------------------
    # The set of choices for fast membership testing
    items_set = Property(depends_on=['items[]'])

    @cached_property
    def _get_items_set(self):
        return set(self.items)

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    @on_trait_change('value, to_string, items[]')
    def _update_value(self):
        self.set_value()

    @on_trait_change('to_string, items[]')
    def _update_items(self):
        self.set_items()

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    def _on_selected(self, event):
        idx = self.widget.GetCurrentSelection()
        value = self.items[idx]
        self.value = value
        self.selected = value
        event.Skip()

    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_items(self):
        str_items = map(self.to_string, self.items)
        self.widget.SetItems(str_items)

    def set_value(self):
        value = self.value
        if value not in self.items_set:
            # This forces a deselection albeit through expensive means
            # for large combo boxes. But, there is no deselect method '
            # on the wx.ComboBox. Hooray wx!
            self.widget.SetItems(self.widget.GetItems())
        else:
            str_value = self.to_string(value)
            self.widget.SetValue(str_value)

