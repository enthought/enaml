#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.async.async_pipe import AsyncSendPipe, AsyncRecvPipe
from enaml.async.async_reply import AsyncReply, MessageFailure

from .qt.QtCore import QObject, Qt, Signal, Slot


class QtLocalPipe(QObject):
    """ A QObject subclass which implements the async pipe interfaces
    and provides the message passing facilities for a local Qt
    application.

    """
    #: The private signal used by the broker to queue work.
    _receive = Signal(object)

    def __init__(self):
        super(QtLocalPipe, self).__init__()
        self._callback = None
        self._cancelled = set()
        self._receive.connect(self._on_receive, Qt.QueuedConnection)

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
    def _on_receive(self, queued_msg):
        """ A private signal handler which dispatches a queued message
        to the receiver, if provided. If no receiver is available the
        reply will be None.

        """
        ctxt, reply = queued_msg

        cancelled = self._cancelled
        if reply in cancelled:
            cancelled.remove(reply)
            return
        
        callback = self._callback
        if callback is not None:
            try:
                result = callback(ctxt)
            except Exception as exc:
                # XXX better exception message trapping
                result = MessageFailure(ctxt, exc.message)
        else:
            result = None

        reply.finished(result)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def put(self, ctxt):
        """ Place a message into the queue for later delivery.

        Parameters
        ----------
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
        reply = AsyncReply(self._cancel_message)
        queued_msg = (ctxt, reply)
        self._receive.emit(queued_msg)
        return reply

    def set_callback(self, callback):
        """ Set the callback for the receiving end of this pipe.

        Parameters
        ----------
        callback : callable
            The callable to be invoked when a message is available
            for receiving. It will be passed two arguments: the
            string message name, and the dictionary message context.
            The return value of the callback is the return value
            for the message.

        """
        self._callback = callback


AsyncSendPipe.register(QtLocalPipe)
AsyncRecvPipe.register(QtLocalPipe)

