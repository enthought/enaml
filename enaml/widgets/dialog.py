#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Instance, Property

from .window import Window, AbstractTkWindow

from ..core.trait_types import EnamlEvent
from ..enums import DialogResult, Modality


class AbstractTkDialog(AbstractTkWindow):
    """ The abstract toolkit interface for a Dialog.

    """
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
    opened = EnamlEvent

    #: Fired when the dialog is closed. The event payload will be the 
    #: dialog result.
    closed = EnamlEvent

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

    #: Overridden parent class trait.
    abstract_obj = Instance(AbstractTkDialog)
    
    #: An internal trait used to store the active state of the dialog.
    _active = Bool(False)

    #: An internal trait used to store the result of the dialog.
    _result = DialogResult('rejected')
        
    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get_active(self):
        """ The property getter for the 'active' attribute.

        """
        return self._active

    def _get_result(self):
        """ The property getter for the 'result' attribute.

        """
        return self._result

    #--------------------------------------------------------------------------
    # Abstract Method Implementations
    #--------------------------------------------------------------------------
    def show(self, parent=None):
        """ Make the dialog visible on the screen.

        If the dialog is not already fully initialized, then the 'setup'
        method will be called prior to making the dialog visible.

        Parameters
        ----------
        parent : native toolkit widget, optional
            Provide this argument if the dialog should have another
            widget as its logical parent. This may help with stacking
            order and/or visibility hierarchy depending on the toolkit
            backend.

        """
        app = self.toolkit.app
        app.initialize()
        if not self.initialized:
            self.setup(parent)
            self.resize_to_initial()
            self.update_minimum_size()
            self.update_maximum_size()
        # Note that we don't start the event loop after making a Dialog
        # visible. Dialogs are shown modally and typically start their 
        # own event loop. Thus, set_visble(True) will block and starting
        # an event loop after it returns may cause a dead lock.
        #
        # XXX pumping the event loop here is a bit of hack. The trick
        # we used on main window doesn't work here because the set
        # visible call actually starts the event loop, we can probably
        # do better.
        for _ in range(10):
            app.process_events()
        self.set_visible(True)
        
    def hide(self):
        """ Close the dialog. Typically, code should call either 'accept'
        or 'reject' to close the dialog instead of 'hide'.

        """
        self.set_visible(False)

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def accept(self):
        """ Close the dialog and set the result to `accepted`.

        Call this method to trigger the same behavior as clicking on an
        Ok button.

        """
        self.abstract_obj.accept()

    def reject(self):
        """ Close the dialog and set the result to `rejected`.

        Call this method to trigger the same behavior as clicking on a
        Cancel button.

        """
        self.abstract_obj.reject()

