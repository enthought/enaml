#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .abstract_button import AbstractButton
from .menu import Menu


class PushButton(AbstractButton):
    """ A button control represented by a standard push button widget.

    """
    #: A read only property which returns the button's menu.
    menu = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_menu(self):
        """ The getter for the 'menu' property.

        Returns
        -------
        result : Menu or None
            The menu for the PushButton, or None if not provided.

        """
        menu = None
        for child in self.children:
            if isinstance(child, Menu):
                menu = child
        return menu

