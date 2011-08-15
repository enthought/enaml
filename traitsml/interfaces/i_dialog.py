from traits.api import Event, Enum, Bool

from .i_window import IWindow

from ..enums import DialogResult


class IDialog(IWindow):
    """ A basic dialog widget whose contents are user defined. 

    The basic dialog has no buttons, but provides methods for 
    the accept and reject behavior for the dialog. Dialogs
    respect the window modality with regards to the application
    of value changes. XXX - describe this more
    
    Attributes
    ----------
    active : Bool
        Set to True when the dialog is open, False otherwise.

    opened : Event
        Fired when the dialog is opened.

    closed : Event
        Fired when the dialog is closed. The args object will
        contain the dialog result.

    result : DialogResult Enum value.
        When the dialog is closed this value is updated to the 
        result of the dialog; REJECTED if Cancel was pressed,
        ACCEPTED if Ok was pressed. The result is set before
        the 'closed' event is fired.
    
    Methods
    -------
    open()
        Open and display the dialog.

    accept()
        Close the dialog and set the result to DialogResult.ACCEPTED.

    reject()
        Close the dialog and set the result to DialogResult.REJECTED.

    """
    active = Bool

    opened = Event

    closed = Event

    result = Enum(*DialogResult.values())

    def open(self):
        """ Open and display the dialog.

        Call this method to launch the dialog.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        DialogError
            Any reason the dialog cannot be opened.

        """
        raise NotImplementedError

    def accept(self):
        """ Close the dialog and set the result to DialogResult.ACCEPTED.

        Call this method to trigger the same behavior as clicking 
        on the Ok button.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        DialogError
            The dialog is not open and so cannot be closed.

        """
        raise NotImplementedError

    def reject(self):
        """ Close the dialog and set the result to DialogResult.REJECTED.

        Call this method to trigger the same behavior as clicking
        on the Cancel button.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        DialogError
            The dialog is not open and so cannot be closed.

        """
        raise NotImplementedError

