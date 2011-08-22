from traits.api import Str, Enum, Instance

from .i_component import IComponent
from .i_container import IContainer

from ..enums import Modality


class IWindow(IComponent):
    """ The base window widget. 

    Window widgets hold a container of components and displays it
    in a frame. Only components which inherit from window can
    be shown on the screen.

    Attributes
    ----------
    title : Str
        The title displayed on the window frame.

    modality : Modality Enum value.
        The modality of the window. Default is toolkit specific.

    Methods
    -------
    layout()
        Initialize and layout the window and it's children.

    set_container(container)
        Set the container of child widgets and/or containers for
        this window.

    show(layout=False)
        Make the window visible on the screen.
    
    hide()
        Hide the window, but do not destroy the widgets. 

    """
    title = Str

    modality = Enum(*Modality.values())

    def layout(self):
        """ Initialize and layout the window and it's children.

        Call this method after the object tree has been built
        in order to create and arrange the underlying widgets.
        This must be called at least once prior to calling 
        the 'show' method. It can be called again at a later
        time in order to rebuild the view.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        LayoutError
            Any reason the action cannot be completed.

        """
        raise NotImplementedError

    def set_container(self, container):
        """ Set the container of children for this window.
        
        Calling this method more than once will replace the previous
        container with the provided container.

        Arguments
        ---------
        container : IContainer
            The container of child widgets and/or containers for
            this window.

        Returns
        -------
        None

        Raises
        ------
        None

        """
        raise NotImplementedError
        
    def show(self, layout=False):
        """ Make the window visible on the screen.

        The 'layout' method must be called at least once prior to
        calling this method. Alternatively, the layout keyword can
        be passed as True, which will then cause 'layout' to be 
        called prior to showing the window.

        Arguments
        ---------
        layout : Bool=False
            Set this keyword argument to True if the 'layout' method 
            should be called prior to showing the window.

        Returns
        -------
        result : None

        Raises
        ------
        LayoutError
            The 'layout' method was not called prior to calling this
            method.

        WindowError
            Any other reason the action cannot be completed.

        """
        raise NotImplementedError

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
        raise NotImplementedError

