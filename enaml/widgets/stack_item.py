#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .container import Container
from .widget import Widget


class StackItem(Widget):
    """ A widget which can be used as an item in a Stack.

    A StackItem is a widget which can be used as a child of a Stack
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    #: A read only property which returns the items's stack widget.
    stack_widget = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_stack_widget(self):
        """ The getter for the 'stack_widget' property.

        Returns
        -------
        result : Container or None
            The stack widget for the StackItem, or None if not provided.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

