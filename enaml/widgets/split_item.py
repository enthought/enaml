#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Any, Bool, Range, Property, cached_property

from .container import Container
from .widget import Widget


class SplitItem(Widget):
    """ A widget which can be used as an item in a Splitter.

    A SplitItem is a widget which can be used as a child of a Splitter
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    #: The stretch factor for this item. The stretch factor determines
    #: how much an item is resized relative to its neighbors when the
    #: splitter space is allocated.
    stretch = Range(low=0, value=1)

    #: Whether or not the item can be collapsed to zero width by the
    #: user. This holds regardless of the minimum size of the item.
    collapsible = Bool(True)

    #: A read only property which returns the split widget.
    split_widget = Property(depends_on='children')

    #: This is a deprecated attribute. It should no longer be used.
    preferred_size = Any

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dict of creation attributes for the control.

        """
        snap = super(SplitItem, self).snapshot()
        snap['stretch'] = self.stretch
        snap['collapsible'] = self.collapsible
        return snap

    def bind(self):
        """ Bind the change handlers for the widget.

        """
        super(SplitItem, self).bind()
        self.publish_attributes('stretch', 'collapsible')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_split_widget(self):
        """ The getter for the 'split_widget' property.

        Returns
        -------
        result : Container or None
            The split widget for the SplitItem, or None if not provided.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

