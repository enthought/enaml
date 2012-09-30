#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .widget_component import WidgetComponent


class MdiWindow(WidgetComponent):
    """ A widget which can be used as a window in an MdiArea.

    An MdiWindow is a widget which can be used as an independent window
    in an MdiArea. It can have at most a single child widget which is 
    an instance of WidgetComponent.

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
        result : WidgetComponent or None
            The mdi widget for the MdiWindow, or None if not provided.

        """
        for child in self.children:
            if isinstance(child, WidgetComponent):
                return child

