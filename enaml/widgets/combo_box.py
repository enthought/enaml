#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Int, Property, Unicode, cached_property

from .constraints_widget import ConstraintsWidget


class ComboBox(ConstraintsWidget):
    """ A drop-down list from which one item can be selected at a time.

    Use a combo box to select a single item from a collection of items.

    """
    #: The unicode strings to display in the combo box.
    items = List(Unicode)

    #: The integer index of the currently selected item. If the given 
    #: index falls outside of the range of items, the item will be
    #: deselected.
    index = Int(-1)

    #: A readonly property that will return the currently selected 
    #: item. If the index falls out of range, the selected item will
    #: be the empty string.
    selected_item = Property(Unicode, depends_on=['index', 'items[]'])
    
    #: How strongly a component hugs it's contents' width. ComboBoxes 
    #: hug width weakly, by default.
    hug_width = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attributes for the combo box.

        """
        snap = super(ComboBox, self).snapshot()
        snap['items'] = self.items
        snap['index'] = self.index
        return snap

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

