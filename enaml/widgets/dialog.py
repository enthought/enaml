#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, Enum

from .window import Window


class Dialog(Window):
    """ A Window subclass which adds modal style behavior.

    The basic dialog has no buttons, but provides methods for the
    accept and reject behavior for the dialog.

    """
    #: An enum which indicates the modality of the dialog. One of 
    #: 'application_modal' or 'window_modal'. The default value is 
    #: 'application_modal'. Changes to this attribute *after* the 
    #: dialog is shown will have no effect.
    modality = Enum('application_modal', 'window_modal')

    #: A read only property which is set to the result of the dialog; 
    #: 'rejected' if rejected() was called or the window was closed via 
    #: the 'x' window button, 'accepted' if accept() was called. The 
    #: result is set before the 'closed' event is fired.
    result = Property(depends_on='_result')

    #: An internal trait used to store the result of the dialog.
    _result = Enum('rejected', 'accepted')
        
    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get_result(self):
        """ The property getter for the 'result' attribute.

        """
        return self._result
   
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the creation attributes for a Dialog

        """
        snap = super(Dialog, self).snapshot()
        snap['modality'] = self.modality
        return snap

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_event_closed(self, payload):
        """ An overridden handler for the 'event-closed' message from 
        the client. The pulls the dialog result out of the payload. 

        """
        result = payload['result']
        self._result = result
        self.closed(result)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def accept(self):
        """ Close the dialog and set the result to `accepted`.

        Call this method to trigger the same behavior as clicking on an
        Ok button.

        """
        self.send_message({'action': 'accept'})

    def reject(self):
        """ Close the dialog and set the result to `rejected`.

        Call this method to trigger the same behavior as clicking on a
        Cancel button.

        """
        self.send_message({'action': 'reject'})

