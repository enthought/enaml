#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Either, Int, Property, cached_property

from .container import Container
from .widget import Widget


class SplitItem(Widget):
    """ A widget which can be used as an item in a Splitter.

    A SplitItem is a widget which can be used as a child of a Splitter
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    #: The preferred size for this item in the splitter, or None if
    #: there is no preference for the size. The default is None.
    preferred_size = Either(None, Int)

    #: A read only property which returns the split widget.
    split_widget = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dict of creation attributes for the control.

        """
        snap = super(SplitItem, self).snapshot()
        snap['preferred_size'] = self.preferred_size
        return snap

    def bind(self):
        """ Bind the change handlers for the widget.

        """
        super(SplitItem, self).bind()
        self.publish_attributes('preferred_size')

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

