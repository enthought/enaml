#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QObject, Signal, Qt
from .qt_registry import qt_lookup


class QHub(QObject):
    """ A QObject subclass which implements an asynchronous hub
    via Qt signals.

    """
    #: A signal that should be emitted by a Qt messenger when it
    #: wishes to send a message to its Enaml peer. A Qt application
    #: should connect to this signal to listen for messages to send
    #: to the Enaml widgets.
    post_message = Signal(object)

    #: A signal that should be emitted by a Qt application when there
    #: is a message that should be delivered to a Qt messenger.
    deliver_message = Signal(object)

    def __init__(self):
        """ Initialize a QHub.

        """
        super(QHub, self).__init__()
        conn = Qt.QueuedConnection
        self.deliver_message.connect(self._on_deliver_message, conn)

    def _on_deliver_message(self, message):
        """ Deliver a message to the Qt messenger target.

        Parameters
        ----------
        message : dict
            A message conforming to the Enaml messaging protocol.

        """
        target_id = message['target_id']
        messenger = qt_lookup(target_id)
        if messenger is not None:
            messenger.receive(message)


#: A singleton Hub instance used by the Qt application to route 
#: messages to and from the Qt messengers.
qt_message_hub = QHub()

