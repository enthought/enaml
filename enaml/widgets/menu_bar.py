#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .menu import Menu
from .widget import Widget


class MenuBar(Widget):
    """ A widget used as a menu bar in a MainWindow.

    """
    @property
    def menus(self):
        """ A property which returns the menus defined on the menu bar.

        """
        isinst = isinstance
        menus = (child for child in self.children if isinst(child, Menu))
        return tuple(menus)

