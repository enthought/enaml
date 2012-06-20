#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple
from uuid import uuid4

from async_application import AsyncApplication, AsyncApplicationError
from async_reply import AsyncReply, MessageFailure

from enaml.backends.qt.qt.QtGui import QApplication
from enaml.backends.qt.qt.QtCore import Qt, Signal, Slot


QueuedMessage = namedtuple('QueuedMessage', 'msg_id msg ctxt reply')


class QtQueuedMessagingApp(QApplication):
    """ A custom QApplication object which provides a queued signals
    for async message dispatching.

    """
    #: A signal emitted when the application should deliver a message
    #: from a messenger to a client object. The payload of the signal 
    #: should be a QueuedMessage instance.
    send_client_message = Signal(object)

    #: A signal emitted when the application should deliver a message
    #: from a client object to a messenger. The payload of the signal 
    #: should be a QueuedMessage instance.
    recv_client_message = Signal(object)


class QtLocalApplication(AsyncApplication):
    """ An Enaml AsyncApplication which executes in the local process
    and uses Qt to create the client widgets.

    """
    def __init__(self):
        self._messengers = {}
        self._clients = {}
        self._cancelled_msgs = set()
        self._qapp = QtQueuedMessagingApp([])
        self._qapp.send_client_message.connect(
            self.on_send_message, Qt.QueuedConnection,
        )
        self._qapp.recv_client_message.connect(
            self.on_recv_message, Qt.QueuedConnection
        )

    def _cancel_msg(self, async_reply):
        self._cancelled_msgs.add(async_reply)

    #--------------------------------------------------------------------------
    # Abstract API implementation
    #--------------------------------------------------------------------------
    def register(self, messenger, id_setter):
        msg_id = uuid4().hex
        self._messengers[msg_id] = messenger
        id_setter(msg_id)

    def send_message(self, msg_id, msg, ctxt):
        if msg_id not in self._clients:
            raise AsyncApplicationError('Client not found')
        reply = AsyncReply(self._cancel_msg)
        queued_msg = QueuedMessage(msg_id, msg, ctxt, reply)
        self._qapp.send_client_message.emit(queued_msg)
        return reply

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    @Slot(object)
    def on_send_command(self, queued_msg):
        """ A slot which is invoked asynchronously with a queued message
        to be delivered from a messenger to a client.

        Parameters
        ----------
        queued_msg : QueuedMessage
            The queued message instance to be processed.

        """
        msg_id, msg, ctxt, reply = queued_msg
        if reply in self._cancelled_msgs:
            self._cancelled_msgs.remove(reply)
            return

        try:
            client = self._clients[msg_id]
        except KeyError:
            raise AsyncApplicationError('Client not found')
        
        try:
            result = client.recv(msg, ctxt)
        except Exception as exc:
            # XXX better exception message trapping
            result = MessageFailure(msg_id, msg, ctxt, exc.message)

        reply.finished(result)

    @Slot(object)
    def on_recv_command(self, queued_msg):
        """ A slot which is invoked asynchronously with a queued message
        to be delivered from a client to a messenger.

        Parameters
        ----------
        queued_msg : QueuedMessage
            The queued message instance to be processed.

        """
        msg_id, msg, ctxt, reply = queued_msg
        if reply in self._cancelled_msgs:
            self._cancelled_msgs.remove(reply)
            return

        try:
            messenger = self._messengers[msg_id]
        except KeyError:
            raise AsyncApplicationError('Messenger not found')
        
        try:
            result = messenger.recv(msg, ctxt)
        except Exception as exc:
            # XXX better exception message trapping
            result = MessageFailure(msg_id, msg, ctxt, exc.message)

        reply.finished(result)

