#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Int, Property, Unicode, cached_property

from .constraints_widget import ConstraintsWidget


class ComboBox(ConstraintsWidget):
    """ A drop-down list from which one item can be selected at a time.

    Use a combo box to select a single item from a collection of items.

    The combo box works by first using the to_string callable to convert
    the value and the list of items into strings for display and then 
    using the index of the combo box to make appropriate selections.

    .. note::
        - If a value is specified that does not exist in the list of
          items then the box is deselected and the index attribute will
          be set to -1. However, the value attribute will still be 
          assigned the invalid value.
        - If list of items is changed then component will try to find
          the current value in the list and select it. If the value is
          not found then the index will be updated to -1.
        - The selected event is only emitted when the user selects
          a valid value through the ui control, not when the value
          is changed programmatically.

    """
    #: The strings to display in the combo box.
    items = List(Unicode)

    #: The integer index of the current selection in items. If the 
    #: given index falls outside of the range of items, no item will
    #: be selected.
    index = Int(-1)

    #: A readonly property that will return the selected item
    selected_item = Property(Unicode, depends_on=['index', 'items[]'])
    
    #: How strongly a component hugs it's contents' width. ComboBoxes hug 
    #: width weakly, by default.
    hug_width = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Returns the dict of creation attributes for the combo box.

        """
        super_attrs = super(ComboBox, self).creation_attributes()
        super_attrs['items'] = self.items
        super_attrs['index'] = self.index
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ComboBox, self).bind()
        self.publish_attributes('items', 'index')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_event_changed(self, payload):
        """ The message handler for the 'event-changed' action from the 
        client widget. The payload will contain the selected 'index'.

        """
        index = payload['index']
        self.set_guarded(index=index)

    #--------------------------------------------------------------------------
    # Property Handlers
    #--------------------------------------------------------------------------
    @cached_property
    def _get_selected_item(self):
        """ The default value handler for :attr:`selected_item`.

        """
        items = self.items
        idx = self.index
        if idx < 0 or idx >= len(items):
            return u''
        return items[idx]

