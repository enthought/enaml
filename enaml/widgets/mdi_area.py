#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .constraints_widget import ConstraintsWidget
from .mdi_window import MdiWindow


class MdiArea(ConstraintsWidget):
    """ A widget which acts as a virtual window manager for other
    top level widget.

    An MdiArea can be used to provide an area within an application
    that can display other widgets in their own independent windows.
    Children of an MdiArea should be defined as instances of MdiWindow.

    """
    #: A read only property which returns the area's MdiWindows.
    mdi_windows = Property(depends_on='children')

    #: An MdiArea expands freely in width and height by default.
    hug_width = 'ignore'
    hug_height = 'ignore'
    
    #: An MdiArea resists clipping only weakly by default.
    resist_width = 'weak'
    resist_height = 'weak'

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_mdi_windows(self):
        """ The getter for the 'mdi_windows' property.

        Returns
        -------
        result : tuple
            The tuple of MdiWindow instances defined as children of this
            MdiArea.

        """
        isinst = isinstance
        windows = (c for c in self.children if isinst(c, MdiWindow))
        return tuple(windows)

