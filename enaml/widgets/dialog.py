#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Event, Bool, Instance, Property

from .window import Window, AbstractTkWindow

from ..enums import DialogResult, Modality


class AbstractTkDialog(AbstractTkWindow):

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
    #: A read only property which will be True when the dialog is open, 
    #: False otherwise.
    active = Property(Bool, depends_on='_active')

    #: Fired when the dialog is opened.
    opened = Event

    #: Fired when the dialog is closed. The event payload will be the 
    #: dialog result.
    closed = Event

    #: A read only property which is set to the result of the dialog; 
    #: 'rejected' if rejected() was called or the window was closed via 
    #: the 'x' window button, 'accepted' if accept() was called. The 
    #: result is set before the 'closed' event is fired.
    result = Property(DialogResult, depends_on='_result')

    #: An enum which indicates the modality of the dialog. One of 
    #: 'application_modal' or 'window_modal'. The default value is 
    #: 'application_modal'. Changes to this attribute *after* the 
    #: dialog is shown will have no effect.
    modality = Modality

    #: An internal trait used to store the active state of the dialog.
    _active = Bool

    #: An internal trait used to store the result of the dialog.
    _result = DialogResult('rejected')

    #: Overridden parent class trait.
    abstract_obj = Instance(AbstractTkDialog)

    def show(self, parent=None):
        """ Make the dialog visible on the screen.

        This is overridden from Window.show(). Since dialogs are shown
        modally by creating their own event loop, there is no need to
        start the event loop at the end of this method as in Window.

        """
        # XXX this may need to be revisited in the future as we get
        # more exposure to dialogs.
        app = self.toolkit.create_app()
        if not self.initialized:
            self.setup(parent)
            # For now, compute the initial size based using the minimum
            # size routine from the layout. We'll probably want to have
            # an initial_size optional attribute or something at some point.
            size = self.layout_manager.calc_min_size()
            if size == (0, 0):
                size = (200, 100)
            self.resize(*size)
        self.set_visible(True)

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
        """ The property getter for the 'active' attribute.

        """
        return self._active

    def _get_result(self):
        """ The property getter for the 'result' attribute.

        """
        return self._result

