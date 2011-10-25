#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Str, Enum, List, Instance

from .component import Component, AbstractTkComponent
from .container import Container

from ..enums import Modality


class AbstractTkWindow(AbstractTkComponent):

    @abstractmethod
    def show(self):
        """ Make the window visible on the screen.

        """
        raise NotImplementedError
    
    @abstractmethod
    def hide(self):
        """ Hide the window from the screen.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_title_changed(self, title):
        raise NotImplementedError
    
    @abstractmethod
    def shell_modality_changed(self, modality):
        raise NotImplementedError


class Window(Component):
    """ The base top-level window widget. 

    Window widgets are top-level components which contain zero or one
    Containers and provide window frame decorations and other window 
    related functionality. Only components which inherit from window 
    can be shown on the screen.

    """
    #: The title displayed on the window frame.
    title = Str

    #: The modality of the window. Default is toolkit specific.
    modality = Enum(*Modality.values())

    #--------------------------------------------------------------------------
    # Overridden parent class traits
    #--------------------------------------------------------------------------
    abstract_widget = Instance(AbstractTkWindow)

    #: The list of children for the window. The list is restricted to 
    #: be length-1 with a child of type Container.
    children = List(Instance(Container), maxlen=1)

    def add_child(self, child):
        self.children.append(child)

    def show(self):
        """ Make the window visible on the screen.

        If the 'setup' method is not explicity called prior to calling
        this method, then the window will lay itself out (with no parent)
        prior to displaying itself to the screen.

        """
        # XXX we shouldn't need to .setup() every time. And get rid 
        # of this qt testing hack
        self.setup()
        self.abstract_widget.widget.resize(640, 480)
        self.abstract_widget.show()

    def hide(self):
        """ Hide the window, but do not destroy the underlying widgets.

        Call this method to hide the window on the screen. This call
        will always succeed.

        """
        self.abstract_widget.hide()

