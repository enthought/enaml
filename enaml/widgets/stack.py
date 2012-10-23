#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Dict, Int, Property, cached_property

from .constraints_widget import ConstraintsWidget
from .stack_item import StackItem


class Stack(ConstraintsWidget):
    """ A component which displays its children as a stack of widgets,
    only one of which is visible at a time.

    """
    #: The index of the visible widget in the stack. The widget itself
    #: does not provide a means to changing this index. That control
    #: must be supplied externally. If the given index falls outside of
    #: the range of stack items, no widget will be visible.
    index = Int(0)

    #: The transition to use when change between stack items.
    #: XXX Document the supported transitions.
    transition = Dict

    #: A read only property which returns the stack's StackItems
    stack_items = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot for the control.

        """
        snap = super(Stack, self).snapshot()
        snap['index'] = self.index
        snap['transition'] = self.transition
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Stack, self).bind()
        self.publish_attributes('index', 'transition')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_index_changed(self, content):
        """ Handle the `index_changed` action from the client widget.

        """
        with self.loopback_guard('index'):
            self.index = content['index']

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_stack_items(self):
        """ The getter for the 'stack_items' property.

        Returns
        -------
        result : tuple
            The tuple of StackItem instances defined as children of
            this Stack.

        """
        isinst = isinstance
        items = (child for child in self.children if isinst(child, StackItem))
        return tuple(items)

