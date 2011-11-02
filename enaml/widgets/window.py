#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Str, Enum, Instance

from .container import Container, AbstractTkContainer


class AbstractTkWindow(AbstractTkContainer):
    """ The abstract Window interface.

    """
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
        """ Update the title of the window with the new value from the
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_modality_changed(self, modality):
        """ Update the window modality with the new value from the
        shell object

        """
        raise NotImplementedError


class Window(Container):
    """ The base top-level Window widget.

    Window widgets are top-level components which provide window frame
    decorations and other window  related functionality. Only components
    which inherit from Window can be shown on the screen. A Window is
    not expected to have a parent in most cases.

    """
    #: The title displayed on the window frame.
    title = Str

    #: The modality of the window.
    modality = Enum('non_modal', 'modal', 'app_modal')

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkWindow)

    def show(self):
        """ Make the window visible on the screen.

        If the 'setup' method is not explicity called prior to calling
        this method, then the window will lay itself out prior to
        displaying itself to the screen.

        """
        # XXX we shouldn't need to .setup() every time.
        self.setup()

        # For now, compute the initial size based using the minimum
        # size routine from the layout. We'll probably want to have
        # an initial_size optional attribute or something at some point.
        size = self.layout.calc_min_size()
        self.resize(*size)
        self.abstract_obj.show()

    def hide(self):
        """ Hide the window, but do not destroy the underlying widgets.

        Call this method to hide the window on the screen. This call
        will always succeed.

        """
        self.abstract_obj.hide()

