from traits.api import Str, Enum

from .i_component import IComponent

from ..enums import Modality


class IWindow(IComponent):
    """ The base top-level window widget. 

    Window widgets are top-level components which provide window frame
    decorations and related functionality. Windows accept any number of
    child IPanels and arrange them according to their own specified
    behavior. The base Window arranges its child panels vertically.
    Only components which inherit from window can be shown on the screen.

    Attributes
    ----------
    title : Str
        The title displayed on the window frame.

    modality : Modality Enum value.
        The modality of the window. Default is toolkit specific.

    Methods
    -------
    set_panel(panel)
        Set the child panel for the window.
    
    layout(parent)
        Layout the components of the ui tree for this window.

    show()
        Make the window visible on the screen.
    
    hide()
        Hide the window, but do not destroy the widgets. 

    """
    title = Str

    modality = Enum(*Modality.values())

    def set_panel(self, panel):
        """ Set the child panel for the window.

        Arguments
        ---------
        panel : IPanel
            The child panel to set.

        Returns
        -------
        None

        """
        raise NotImplementedError

    def layout(self, parent):
        """ Layout the components of the ui tree for this window.

        Arguments
        ---------
        parent : IComponent or None
            The parent of this window.
        
        Returns
        -------
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

