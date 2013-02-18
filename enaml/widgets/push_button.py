#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .abstract_button import AbstractButton
from .menu import Menu


class PushButton(AbstractButton):
    """ A button control represented by a standard push button widget.

    """
    @property
    def menu(self):
        """ A property which returns the button menu, if defined.

        """
        menu = None
        for child in self.children:
            if isinstance(child, Menu):
                menu = child
        return menu

