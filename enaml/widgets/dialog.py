#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Event, Enum, Bool, Instance, Property

from .window import IWindowImpl, Window

from ..enums import DialogResult

# XXX punting for now, but this needs to be brought up-to-date

class IDialogImpl(IWindowImpl):

    def open(self):
        raise NotImplementedError

    def accept(self):
        raise NotImplementedError
    
    def reject(self):
        raise NotImplementedError


class Dialog(Window):
    """ A basic dialog widget whose contents are user defined. 

    The basic dialog has no buttons, but provides methods for the 
    accept and reject behavior for the dialog.
    
    Attributes
    ----------
    active : Property(Bool)
        A read only property which will be True when the dialog is open,
        False otherwise.

    opened : Event
        Fired when the dialog is opened.

    closed : Event
        Fired when the dialog is closed. The event payload will be the
        dialog result.

    result : Property(Enum(*DialogResult.values())).
        A read only property which is set to the result of the dialog; 
        REJECTED if rejected() was called or the window was closed via 
        the 'x' window button, ACCEPTED if accept() was called. The 
        result is set before the 'closed' event is fired.
    
    _shadow : Bool
        A protected attribute used by the implementation object to
        set the value of the active attribute.
    
    _shadow : Enum(*Dialog.values())
        A protected attribute used by the implementation object to
        set the value of the result attribute.

    Methods
    -------
    open()
        Open and display the dialog.

    accept()
        Close the dialog and set the result to DialogResult.ACCEPTED.

    reject()
        Close the dialog and set the result to DialogResult.REJECTED.

    """
    active = Property(Bool, depends_on='_active')

    opened = Event

    closed = Event

    result = Property(Enum(*DialogResult.values()), depends_on='_result')

    _active = Bool

    _result = Enum(*DialogResult.values())

    #: Overridden parent class trait
    toolkit_impl = Instance(IDialogImpl)
    
    def open(self):
        """ Open and display the dialog.

        Call this method to launch the dialog.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.open()

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

        """
        self.toolkit_impl.accept()

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

        """
        self.toolkit_impl.reject()

    def _get_active(self):
        return self._active
    
    def _get_result(self):
        return self._result


Dialog.protect('_active', '_result', 'opened', 'closed', 'result', 'active')

