#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Property, cached_property

from .constraints_widget import ConstraintsWidget
from .container import Container


#: Enum trait describing the scrollbar policies that can be assigned to 
#: the horizontal and vertical scrollbars.
ScrollbarPolicy = Enum('as_needed', 'always_on', 'always_off')


class ScrollArea(ConstraintsWidget):
    """ A widget which displays a single child in a scrollable area.

    A ScrollArea has at most a single child Container widget.

    """
    #: The horizontal scrollbar policy.
    horizontal_scrollbar = ScrollbarPolicy

    #: The vertical scrollbar policy.
    vertical_scrollbar = ScrollbarPolicy

    #: A read only property which returns the scroll area's scroll 
    #: widget.
    scroll_widget = Property(depends_on='children[]')

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
        snap['scroll_widget_id'] = self._snap_scroll_widget_id()
        snap['horizontal_scrollbar'] = self.horizontal_scrollbar
        snap['vertical_scrollbar'] = self.vertical_scrollbar
        return snap

    def bind(self):
        """ Bind the change handlers for this widget.

        """
        super(ScrollArea, self).bind()
        attrs = ('horizontal_scrollbar', 'vertical_scrollbar')
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_scroll_widget(self):
        """ The getter for the 'scroll_widget' property.

        Returns
        -------
        result : Container or None
            The scroll widget for the ScrollArea, or None if not 
            provided.

        """
        for child in self.children:
            if isinstance(child, Container):
                return child

    def _snap_scroll_widget_id(self):
        """ Returns the widget id for the scroll widget or None.

        """
        scroll_widget = self.scroll_widget
        if scroll_widget is not None:
            return scroll_widget.widget_id

