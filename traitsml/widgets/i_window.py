from traits.api import Str, Enum

from .i_component import IComponent

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
    layout(parent=None)
        Initialize and layout the window and it's children.

    set_container(container)
        Set the container of child widgets and/or containers for
        this window.

    show()
        Make the window visible on the screen.
    
    hide()
        Hide the window, but do not destroy the widgets. 

    """
    title = Str

    modality = Enum(*Modality.values())

    def layout(self, parent=None):
        """ Initialize and layout the window and it's children.

        Call this method after the object tree has been built
        in order to create and arrange the underlying widgets.
        This must be called at least once prior to calling 
        the 'show' method. It can be called again at a later
        time in order to rebuild the view.

        Arguments
        ---------
        parent : IComponent, optional
            The parent component of this window, if any. Defaults 
            to None. This is only really useful if you want complex 
            modal interactions between windows that respects the
            parent/child heierarchy. The parent should have already
            been layed out (and therefore have created its internal
            widget) before being passed in to this method.

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
        
    def get_container(self):
        """ Return the container of children for this window.

        Call this method to retrieve the container previously 
        set with set_container.

        Arguments
        ---------
        None

        Returns
        -------
        result : IContainer or None
            Returns the conainter set on this window if one is set.

        Raises
        ------
        None

        """
        raise NotImplementedError
        
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

