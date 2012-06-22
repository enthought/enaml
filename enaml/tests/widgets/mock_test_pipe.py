from threading import Condition, Thread

from enaml.async.async_pipe import AsyncRecvPipe, AsyncSendPipe
from enaml.async.async_reply import AsyncReply, MessageFailure


class MockTestPipe(object):
    def __init__(self):
        self._callback = None
        self._cancelled = set()
        self._messages = list()
        self._queue_lock = Condition()

    #--------------------------------------------------------------------------
    # Private Api
    #--------------------------------------------------------------------------
    def _cancel_message(self, reply):
        self._cancelled.add(reply)

    def _process(self, queued_msg):
        msg, ctxt, reply = queued_msg

        cancelled = self._cancelled
        if reply in cancelled:
            cancelled.remove(reply)
            return

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

    def _main_loop(self):
        """ Run the main loop of this messenger.

        """
        ql = self._queue_lock

        while True:
            ql.acquire()
            if len(self._messages) == 0:
                ql.wait()
            message = self._messages.pop(0)
            ql.release()
            # Call _process outside of the lock since the receiver might try to
            # send a message.
            self._process(message)

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
        reply = AsyncReply(self._cancel_message)
        queued_msg = (msg, ctxt, reply)
        ql = self._queue_lock
        ql.acquire()
        self._messages.append(queued_msg)
        ql.notify()
        ql.release()
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

    def run(self):
        """ Run the message pipe in a thread for asyncronicity
        """
        self.thread = Thread(target=self._main_loop)
        self.thread.daemon = True
        self.thread.start()


AsyncSendPipe.register(MockTestPipe)
AsyncRecvPipe.register(MockTestPipe)

