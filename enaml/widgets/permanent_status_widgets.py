#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from enaml.core.messenger import Messenger
from .widget import Widget

class PermanentStatusWidgets(Messenger):
    """ A non-visible goruping  used to contain the permanent members of a StatusBar

    """
    #: A read only property which returns the status bar's permanent widgets.
    widgets = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_widgets(self):
        """ The getter for the 'widgets' property.

        Returns
        -------
        result : tuple
            The tuple of Widgets defined as children of this PermanentStatusWidget.

        """
        isinst = isinstance
        widgets = (child for child in self.children if isinst(child, Widget))
        return tuple(widgets)

