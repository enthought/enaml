from traits.api import Str, Enum

from .i_panel import IPanel

from ..enums import Modality


class IWindow(IPanel):
    """ The base top-level window widget. 

    Window widgets are top-level panels which provide window frame
    decorations and related functionality. Only components which 
    inherit from window can be shown on the screen.

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

