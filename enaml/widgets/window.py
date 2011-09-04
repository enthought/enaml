from traits.api import Str, Enum, List, Instance

from .component import Component, IComponentImpl
from .panel import Panel

from ..enums import Modality


class IWindowImpl(IComponentImpl):

    def show(self):
        raise NotImplementedError
    
    def hide(self):
        raise NotImplementedError

    def parent_title_changed(self, title):
        raise NotImplementedError
    
    def parent_modality_changed(self, modality):
        raise NotImplementedError


class Window(Component):
    """ The base top-level window widget. 

    Window widgets are top-level components which contain zero or more
    Panels and provide window frame decorations and other window related
    functionality. Only components which inherit from window can be shown
    on the screen.

    Attributes
    ----------
    title : Str
        The title displayed on the window frame.

    modality : Modality Enum value.
        The modality of the window. Default is toolkit specific.

    Methods
    -------
    show()
        Make the window visible on the screen.
    
    hide()
        Hide the window, but do not destroy the widgets. 

    """
    title = Str

    modality = Enum(*Modality.values())

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IWindowImpl)

    children = List(Instance(Panel), maxlen=1)

    def show(self):
        """ Make the window visible on the screen.

        If the 'layout' method is not explicity called prior to calling
        this method, then the window will lay itself out (with no parent)
        prior to displaying itself to the screen.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        WindowError
            Any reason the action cannot be completed.

        """
        self.layout()
        self.toolkit_impl.show()

    def hide(self):
        """ Hide the window, but do not destroy the underlying widgets.

        Call this method to hide the window on the screen. This call
        will always succeed.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        None

        """
        self.toolkit_impl.hide()

