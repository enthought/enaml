#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import WeakValueDictionary

from enaml.async.async_reply import AsyncReply, MessageFailure

from .qt.QtCore import QObject, Qt, Signal, Slot


class QMessageBroker(QObject):
    """ A QObject subclass which acts as a message broker using queued
    signals to dispatch work.

    """
    #: The private signal used by the broker to queue work.
    _process = Signal(object)

    def __init__(self):
        super(QMessageBroker, self).__init__()
        self._receivers = WeakValueDictionary()
        self._cancelled = set()
        self._process.connect(self._on_process, Qt.QueuedConnection)

    #--------------------------------------------------------------------------
    # Private Api
    #--------------------------------------------------------------------------
    def _cancel_message(self, reply):
        """ A private method which is supplied to the generated async
        reply objects so that they may cancel delivery of a message.

        Parameters
        ----------
        reply : AsyncReply
            The async reply instance associated with the message to be
            cancelled.

        """
        self._cancelled.add(reply)

    @Slot(object)
    def _on_process(self, queued_msg):
        """ A private signal handler which dispatches a message to the
        appropriate receiver. 

        If the receiver no longer exists, the message is dropped.

        """
        msg_id, msg, ctxt, reply = queued_msg

        cancelled = self._cancelled
        if reply in cancelled:
            cancelled.remove(reply)
            return

        try:
            receiver = self._receivers[msg_id]
        except KeyError:
            return # Log this instead.
        
        try:
            result = receiver.recv(msg, ctxt)
        except Exception as exc:
            # XXX better exception message trapping
            result = MessageFailure(msg_id, msg, ctxt, exc.message)

        reply.finished(result)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def put(self, msg_id, msg, ctxt):
        """ Place a message into the broker queue for later delivery.

        If there is no receiver registered for the given messaging id,
        then this method is a no-op.

        Parameters
        ----------
        msg_id : string
            The messaging id for the receiver of the message.

        msg : string
            The message to send to the the receiver.

        ctxt : dict
            The context dictionary for the message.

        Returns
        -------
        result : AysncReply
            An async reply instance which can be used to retrieve the
            results of the message handler.

        """
        if msg_id not in self._receivers:
            return
        reply = AsyncReply(self._cancel_message)
        queued_msg = (msg_id, msg, ctxt, reply)
        self._process.emit(queued_msg)
        return reply

    def register(self, msg_id, receiver):
        """ Register a receiver for the given messaging id. 

        Only one receiver may be registered at time. The reference to
        the receiver object is stored weakly.

        """
        self._receivers[msg_id] = receiver

