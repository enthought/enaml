#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .widget import Widget


class MdiWindow(Widget):
    """ A widget which can be used as a window in an MdiArea.

    An MdiWindow is a widget which can be used as an independent window
    in an MdiArea. It can have at most a single child widget which is
    an instance of Widget.

    """
    #: A read only property which returns the pane's dock widget.
    mdi_widget = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_mdi_widget(self):
        """ The getter for the 'mdi_widget' property.

        Returns
        -------
        result : Widget or None
            The mdi widget for the MdiWindow, or None if not provided.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Widget):
                widget = child
        return widget

