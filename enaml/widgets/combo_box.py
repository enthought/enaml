#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, List, Int, Property, Unicode, cached_property

from .control import Control


class ComboBox(Control):
    """ A drop-down list from which one item can be selected at a time.

    Use a combo box to select a single item from a collection of items.

    """
    #: The unicode strings to display in the combo box.
    items = List(Unicode)

    #: The integer index of the currently selected item. If the given
    #: index falls outside of the range of items, the item will be
    #: deselected.
    index = Int(-1)

    #: Whether the text in the combo box can be edited by the user.
    editable = Bool(False)

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
        snap['editable'] = self.editable
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ComboBox, self).bind()
        self.publish_attributes('index', 'editable')
        self.on_trait_change(self._send_items, 'items, items_items')

    def _send_items(self):
        """ Send the 'set_items' action to the client widget.

        """
        content = {'items': self.items}
        self.send_action('set_items', content)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_index_changed(self, content):
        """ The message handler for the 'index_changed' action from the
        client widget. The content will contain the selected 'index'.

        """
        index = content['index']
        self.set_guarded(index=index)

    #--------------------------------------------------------------------------
    # Property Handlers
    #--------------------------------------------------------------------------
    @cached_property
    def _get_selected_item(self):
        """ The getter for the `selected_item` property.

        """
        items = self.items
        idx = self.index
        if idx < 0 or idx >= len(items):
            return u''
        return items[idx]

