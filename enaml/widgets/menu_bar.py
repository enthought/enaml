#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Property, List, Instance, cached_property

from .component import Component, AbstractTkComponent

from .menu import Menu


class AbstractTkMenuBar(AbstractTkComponent):
    """ The abstract toolkit interface for a MenuBar.

    """
    @abstractmethod
    def shell_menus_changed(self, menus):
        """ Update the menu bar with the new list of menu objects.

        """
        raise NotImplementedError


class MenuBar(Component):
    """ A declarative Enaml Component which represents a menu bar in
    a main window.

    """
    #: A read-only cached property which holds the list of children
    #: which are instances of Menu.
    menus = Property(List(Instance(Menu)), depends_on='children')

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkMenuBar)

    @cached_property
    def _get_menus(self):
        """ The property getter for the 'menus' attribute.

        """
        flt = lambda child: isinstance(child, Menu)
        return filter(flt, self.children)

