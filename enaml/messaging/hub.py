#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.core.signaling import Signal

from .registry import lookup


class Hub(object):
    """ A central messaging hub for routing messages to and from
    messengers.

    """
    #: A signal that should be emitted by an Enaml messenger when 
    #: it wishes to send a message to its client peer. Applications
    #: should connect to this signal to listen for messages to send
    #: to their client widgets. Signal handlers will be called on
    #: the same thread as the Enaml messenger.
    post_message = Signal()

    #: A signal that should be emitted by an application when there
    #: is a message that should be delivered to an Enaml messenger.
    #: The message will be delivered on the same thread as the
    #: emitter of the signal.
    deliver_message = Signal()

    def __init__(self):
        """ Initialize a Hub.

        """
        self.deliver_message.connect(self._on_deliver_message)

    def _on_deliver_message(self, message):
        """ Deliver a message to the Enaml messenger target.

        Parameters
        ----------
        message : dict
            A message conforming to the Enaml messaging protocol.

        """
        target_id = message['target_id']
        messenger = lookup(target_id)
        if messenger is not None:
            messenger.receive(message)


#: A singleton Hub instance used by the applications to route messages 
#: to and from Enaml messengers.
message_hub = Hub()

