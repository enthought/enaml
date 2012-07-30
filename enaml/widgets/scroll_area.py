#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum

from .constraints_widget import ConstraintsWidget


#: Enum trait describing the scrollbar policies that can be assigned to 
#: the horizontal and vertical scrollbars.
ScrollbarPolicy = Enum('as_needed', 'always_on', 'always_off')


class ScrollArea(ConstraintsWidget):
    """ A widget which displays a single child in a scrollable area.

    Though any widget can technically be used as the child, currently,
    only a Container is guaranteed to have the correct sizing behavior.

    Only a single child should be provided to a scroll area. Providing
    more than a single child will result in undefined behavior.

    """
    #: The horizontal scrollbar policy.
    horizontal_scrollbar = ScrollbarPolicy

    #: The vertical scrollbar policy.
    vertical_scrollbar = ScrollbarPolicy

    #: How strongly a component hugs it's contents' width. Scroll
    #: areas do not hug their width and are free to expand.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. Scroll
    #: areas do not hug their height and are free to expand.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(ScrollArea, self).snapshot()
        snap['horizontal_scrollbar'] = self.horizontal_scrollbar
        snap['vertical_scrollbar'] = self.vertical_scrollbar
        return snap

    def bind(self):
        """ Bind the change handlers for this widget.

        """
        super(ScrollArea, self).bind()
        attrs = ('horizontal_scrollbar', 'vertical_scrollbar')
        self.publish_attributes(*attrs)

