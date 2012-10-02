#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .container import Container
from .widget_component import WidgetComponent


class SplitItem(WidgetComponent):
    """ A widget which can be used as an item in a Splitter.

    A SplitItem is a widget which can be used as a child of a Splitter
    widget. It can have at most a single child widget which is an 
    instance of Container.

    """
    #: A read only property which returns the split widget.
    split_widget = Property(depends_on='children')

    # XXX expose some configurability here.
    
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
        for child in self.children:
            if isinstance(child, Container):
                return child

