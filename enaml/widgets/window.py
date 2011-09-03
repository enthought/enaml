from traits.api import Str, Enum, Bool, List, Instance, Interface

from .component import Component, IComponentImpl
from .panel import Panel

from ..enums import Modality


class IWindowImpl(IComponentImpl):

    def create_widget(self):
        raise NotImplementedError
    
    def initialize_widget(self):
        raise NotImplementedError

    def layout_child_widgets(self):
        raise NotImplementedError
        
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
    layout(parent)
        Layout the window with the provided parent.

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
    _impl = Instance(IWindowImpl)

    children = List(Instance(Panel), maxlen=1)

    def layout(self):
        """ Layout the children in the window.

        Call this method to initialize the ui tree, which includes the 
        creation of the underlying toolkit widgets. This method will not
        usually be called by user code.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        impl = self._impl
        impl.create_widget()
        for panel in self.children:
            panel.layout()
        impl.initialize_widget()
        impl.layout_child_widgets()
        self._hook_impl()

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
        self._impl.show()

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
        self._impl.hide()

