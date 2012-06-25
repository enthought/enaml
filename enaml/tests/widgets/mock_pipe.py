from threading import Condition, Thread

from enaml.async.async_pipe import AsyncRecvPipe, AsyncSendPipe
from enaml.async.async_reply import AsyncReply, MessageFailure


class MockPipe(object):
    """ A really dumb Async[Send/Recv]Pipe that isn't really asynchronous.

    """

    def __init__(self):
        self._callback = None

    #--------------------------------------------------------------------------
    # Private Api
    #--------------------------------------------------------------------------
    def _process(self, queued_msg):
        msg, ctxt, reply = queued_msg

        callback = self._callback
        if callback is not None:
            try:
                result = callback(msg, ctxt)
            except Exception as exc:
                # XXX better exception message trapping
                result = MessageFailure(msg, ctxt, exc.message)
        else:
            result = None

        reply.finished(result)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def put(self, msg, ctxt):
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
        reply = AsyncReply()
        queued_msg = (msg, ctxt, reply)
        self._process(queued_msg)
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


AsyncSendPipe.register(MockPipe)
AsyncRecvPipe.register(MockPipe)

