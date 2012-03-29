#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Str, Any, Instance

from .container import Container, AbstractTkContainer


class AbstractTkTab(AbstractTkContainer):
    """ The abstract toolkit Tab interface.

    """
    @abstractmethod
    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute on the shell
        object.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_icon_changed(self, icon):
        """ The change handler for the 'icon' attribute on the shell
        object.

        """
        raise NotImplementedError


class Tab(Container):
    """ A Container subclass that represents a tab in a Tabbed container.
    
    """
    #: The title of this tab in the Tabbed container.
    title = Str

    #: The icon displayed on this tab, if any.
    # XXX handle icons!
    icon = Any

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkTab)

    def set_visible(self, foo):
        """ Overridden visibility method which turns off the ability
        to change the visibility of a tab. A Tab's visibility is 
        controlled implicitly by the TabGroup and the currently
        selected tab.

        """
        pass
    
