#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Event, Bool, Instance, Property

from .window import Window, AbstractTkWindow

from ..enums import DialogResult


class AbstractTkDialog(AbstractTkWindow):

    @abstractmethod
    def open(self):
        """ Open and display the dialog.

        """
        raise NotImplementedError

    @abstractmethod
    def accept(self):
        """ Close the dialog and set the result to `accepted`.

        """
        raise NotImplementedError

    @abstractmethod
    def reject(self):
        """ Close the dialog and set the result to `rejected`.

        """
        raise NotImplementedError


class Dialog(Window):
    """ A basic dialog widget whose contents are user defined.

    The basic dialog has no buttons, but provides methods for the
    accept and reject behavior for the dialog.

    """

    #: A read only property which will be True when the dialog is open, False
    #: otherwise.
    active = Property(Bool, depends_on='_active')

    #: Fired when the dialog is opened.
    opened = Event

    #: Fired when the dialog is closed. The event payload will be the dialog
    #: result.
    closed = Event

    #: A read only property which is set to the result of the dialog; 'rejected'
    #: if rejected() was called or the window was closed via the 'x' window
    #: button, 'accepted' if accept() was called. The result is set before the
    #: 'closed' event is fired.
    result = Property(DialogResult, depends_on='_result')

    _active = Bool

    _result = DialogResult('rejected')

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkDialog)

    def open(self):
        """ Open and display the dialog.

        Call this method to launch the dialog.

        """
        self.abstract_obj.open()

    def accept(self):
        """ Close the dialog and set the result to `accepted`.

        Call this method to trigger the same behavior as clicking
        on the Ok button.

        """
        self.abstract_obj.accept()

    def reject(self):
        """ Close the dialog and set the result to `rejected`.

        Call this method to trigger the same behavior as clicking
        on the Cancel button.

        """
        self.abstract_obj.reject()

    def _get_active(self):
        return self._active

    def _get_result(self):
        return self._result

