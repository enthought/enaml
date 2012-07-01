#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class AsyncReply(object):
    """ An async reply object which notifies callbacks when a 'reply'
    is available for a previously made 'request'.

    An async reply is created by an application instance whenever an
    operation of type 'request' is sent to a target. Since the messages
    are delivered asynchronously, this object provides a means by which 
    user code can be notified when the operation is completed.

    A user may register a callback to be executed when the results of 
    the operation are available. A callback can be supplied by calling
    the 'set_callback' method. It will be invoked with the payload of 
    the reply.

    """
    def __init__(self, cancel_request=None):
        """ Initialize an AsyncReply.

        Parameters
        ----------
        cancel_request : callable, optional
            An optional callable that will cancel a request before 
            it has processed by the target. It should accept a single 
            argument, which is this async reply instance.

        """
        self._cancel_request = cancel_request
        self._pending = True
        self._cancelled = False
        self._results = None
        self._callback = None

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _dispatch(self):
        """ Dispatches the results of the message to the appropriate 
        callback or failback, if provided by the user.

        """
        handler = self._callback
        if handler is not None:
            cb, args, kwargs = handler
            # XXX handle exceptions in callbacks?
            cb(self._results, *args, **kwargs) 

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def cancel(self):
        """ Cancel the delivery of the message. 

        If the message is no longer pending, then this operation is a
        no-op. Otherwise, the cancel message callback will be called, 
        and no further dispatching will be performed.

        """
        self._cancelled = True
        if self._pending:
            self._pending = False
            cancel_req = self._cancel_request
            if cancel_req is not None:
                cancel_req(self)

    def finished(self, results):
        """ Called by the application object when the message has
        finished being processed.

        If the command was cancelled, this method is a no-op. Otherwise,
        calling this method more than once is an error.
        
        Parameters
        ----------
        results : object
            The results of the message that was handled by the client
            or a MessageFailure if it was not properly handled.

        """
        if self._cancelled:
            if self._pending:
                self._pending = False
            return
        if not self._pending:
            raise RuntimeError("AsyncReply already finished")
        self._pending = False
        self._results = results
        self._dispatch()

    def pending(self):
        """ Returns whether or not the async command is still pending
        execution.

        Returns
        -------
        result : bool
            True if the command execution is still pending, False 
            otherwise.

        """
        return self._pending

    def results(self):
        """ Returns the results of the async command.

        If the results of the command are not yet available due to the
        command being cancelled or still pending, then this method will 
        raise a ValueError.

        Returns
        -------
        result : object
            The result of the async command.

        """
        if self._pending or self._cancelled:
            raise ValueError('Results not available')
        return self._results

    def set_callback(self, callback, *args, **kwargs):
        """ Set the callback to be run when the request has finished.

        If the message has already finished and was not cancelled, then
        the callback will be invoked immediately with the payload. If 
        the message has been cancelled, this method is a no-op.

        The callback must accept at least one arguments which is the
        payload of the reply.

        Parameters
        ----------
        callback : callable
            A callable which accepts at least one argument which will 
            be the results of the message.

        *args, **kwargs
            Any addional positional or keyword parameters to pass to 
            the callback when it is invoked.

        """
        if self._cancelled:
            return
        self._callback = (callback, args, kwargs)
        if not self._pending:
            self._dispatch()

