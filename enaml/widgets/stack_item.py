#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .container import Container
from .widget_component import WidgetComponent


class StackItem(WidgetComponent):
    """ A widget which can be used as an item in a Stack.

    A StackItem is a widget which can be used as a child of a Stack
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    #: A read only property which returns the items's stack widget.
    stack_widget = Property(depends_on='children[]')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for the control.

        """
        snap = super(StackItem, self).snapshot()
        snap['stack_widget_id'] = self._snap_stack_widget_id()
        return snap

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
        for child in self.children:
            if isinstance(child, Container):
                return child

    def _snap_stack_widget_id(self):
        """ Returns the widget id for the stack widget or None.

        """
        stack_widget = self.stack_widget
        if stack_widget is not None:
            return stack_widget.widget_id

