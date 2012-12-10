#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .menu import Menu
from .widget import Widget


class MenuBar(Widget):
    """ A widget used as a menu bar in a MainWindow.

    """
    #: A read only property which returns the menu bar's menus.
    menus = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_menus(self):
        """ The getter for the 'menus' property.

        Returns
        -------
        result : tuple
            The tuple of Menus defined as children of this MenuBar.

        """
        isinst = isinstance
        menus = (child for child in self.children if isinst(child, Menu))
        return tuple(menus)

