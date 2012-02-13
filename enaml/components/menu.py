#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (
    Instance, Either, Unicode, Property, List, cached_property,
)

from .action import Action
from .component import Component, AbstractTkComponent

from ..core.trait_types import EnamlEvent


class AbstractTkMenu(AbstractTkComponent):
    """ The abstract toolkit interface for a Menu object.

    """
    @abstractmethod
    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute on the shell
        object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_contents_changed(self, contents):
        """ The change handler for the list of contents on the
        shell object.

        """
        raise NotImplementedError
        
    @abstractmethod
    def popup(self, blocking=True):
        """ Create and show the menu as context or popup menu.

        Parameters
        ----------
        blocking : boolean, optional
            Whether or not the popup menu should be displayed in a 
            blocking context. If False, then this menu object must
            be stored on the heap or it will be immediately garbage
            collected. Defaults to True.

        """
        raise NotImplementedError


MenuContents = List(Either(Instance('Menu'), Instance(Action)))


class Menu(Component):
    """ A declarative Enaml Component which represents a menu in a 
    menu bar.

    """
    #: The title of the menu as displayed by a MenuBar
    title = Unicode

    #: An event emitted when the menu is about to be shown.
    about_to_show = EnamlEvent

    #: An event emitted when the menu is about to be hidden.
    about_to_hide = EnamlEvent

    #: A read-only cached property which holds the list of menu
    #: contents which are instances of Menu or Action.
    contents = Property(MenuContents, depends_on='children')

    @cached_property
    def _get_contents(self):
        """ The property getter for the 'contents' attribute.

        """
        flt = lambda child: isinstance(child, (Menu, Action))
        return filter(flt, self.children)

    def popup(self, blocking=True, parent=None):
        """ Create and show the menu as context or popup menu.

        If the menu has not been initialized when this method is
        called, it will be setup and initialized automatically.

        Parameters
        ----------
        blocking : boolean, optional
            Whether or not the popup menu should be displayed in a 
            blocking context. If False, then this menu object must
            be stored on the heap or it will be immediately garbage
            collected. Defaults to True. This option may not be 
            supported on all toolkit backends. 
        
        parent : Toolkit widget or None, optional
            The parent on which to popup the menu. This only has an
            effect on menus which are created outside of the normal 
            Enaml heirarchy and are setup and initialized during the 
            call to this method. Even then, the popup menu will be a 
            top-level widget, but it's lifetime will be tied to that 
            of the parent.

        """
        if not self.initialized:
            self.setup(parent)
        self.abstract_obj.popup(blocking=blocking)

