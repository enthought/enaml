""" NOTES: The combo box elements are read-only, the `opened`
flag doesn't work, and the `value` trait can be set to a string that is
not in `items`. The `value` trait also is currently just the selected string,
not the associated value.

"""

import wx

from traits.api import \
        implements, Dict, Str, Any, Bool, Callable, Event, on_trait_change

from .wx_element import WXElement

from ..i_combo_box import IComboBox


class WXComboBox(WXElement):
    """ A wxPython implementation of IPushButton.

    Use a combo box to select a single item from a collection of
    items. To select multiple items from a collection of items
    use a List widget.
    
    Attributes
    ----------
    items : Dict(Str, Any)
        Maps the string representations of the items in the collection
        to the items themselves.

    value : Any
        The currently selected item from the collection.

    sort : Bool
        Whether or not to sort the choices for display.

    sort_key : Callable
        If sort is True, this sort key will be used. The keys in
        the items dict will be passed as arguments to the key. 
        The default key sorts by ascii order.
    
    opened : Bool
        Set to True when the combo box is opened, False otherwise.

    selected : Event
        Fired when a new selection is made. The args object will
        contain the selection.

    clicked : Event
        Fired when the combo box is clicked.

    """
    implements(IComboBox)


    #===========================================================================
    # IComboBox interface
    #===========================================================================

    items = Dict(Str, Any)

    value = Any

    sort = Bool

    sort_key = Callable(lambda val: val)

    opened = Bool

    selected = Event

    clicked = Event

    #===========================================================================
    # Implementation
    #===========================================================================
    def create_widget(self):
        """ Creates and binds a wx.ComboBox.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Arguments
        ---------
        parent : WXContainer
            The WXContainer instance that is our parent.

        Returns
        -------
        result : None

        """
        widget = wx.ComboBox(self.parent_widget(), style=wx.CB_READONLY)
        widget.Bind(wx.EVT_COMBOBOX, self._on_selected)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_clicked)
        self.widget = widget

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def init_attributes(self):
        """ Intializes the widget with the attributes of this instance.
        
        """
        self.set_items()
        widget = self.widget
        widget.SetSelection(0)
        self.value = widget.GetStringSelection()

    def init_meta_handlers(self):
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    @on_trait_change('items[]')
    def items_trait_changed(self):
        """ Sync the widget with changes to the `self.items` attribute.

        """
        self.set_items()

    def _value_changed(self):
        """ Update the attribute associated with the widget's current selection.

        """
        self.widget.SetValue(self.value)
    
    def _sort_changed(self):
        self.sort_items()
    
    def _sort_key_changed(self):
        self.sort_items()

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    def _on_selected(self, event):
        self.value = self.widget.GetStringSelection()
        self.selected = True
        event.Skip()

    def _on_clicked(self, event):
        self.clicked = True
        event.Skip()

    def set_items(self):
        self.widget.SetItems(self.items.keys())

    def sort_items(self):
        """ Sort the names in the combo box.

        """
        if self.sort:
            items = self.items.keys()
            items.sort(key=self.sort_key)
            self.widget.SetItems(items)
