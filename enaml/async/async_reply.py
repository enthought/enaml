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
    user code can be notified when the operation is completed; i.e.
    a 'reply' operation has been received for a previously 'request'.

    A user may register a callback to be executed when the results of 
    the request are available. A callback can be supplied by calling
    the 'set_callback' method. It will be invoked with the 'results'
    portion of the reply. An error handler can also be set by calling
    the 'set_errback' method. This callback will be invoked with the
    'error' portion of the reply when the request handler on the peer 
    raised an error.

    """
    def __init__(self, op_id, cancel_request=None):
        """ Initialize an AsyncReply.

        Parameters
        ----------
        op_id : str
            The operation id string associated with this reply object.

        cancel_request : callable, optional
            An optional callable that will cancel a request before 
            it has processed by the target. It should accept a single 
            argument, which is this async reply instance.

        """
        self._op_id = op_id
        self._cancel_request = cancel_request
        self._pending = True
        self._cancelled = False
        self._payload = None
        self._callback = None
        self._errback = None
        
    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _dispatch(self):
        """ Dispatches the results of the message to the appropriate 
        callback or failback, if provided by the user.

        """
        payload = self._payload
        error = payload['error']
        if error is not None:
            handler = self._errback
            res = error
        else:
            handler = self._callback
            res = payload['results']
        if handler is not None:
            cb, args, kwargs = handler
            cb(res, *args, **kwargs) 

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @property
    def op_id(self):
        """ A read only property which returns the operation id 
        which is associated with this async reply.

        """
        return self._op_id

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

    def finished(self, payload):
        """ Called by the application object when the 'reply' to a 
        previous 'request' is received.

        If the command was cancelled, this method is a no-op. Otherwise,
        calling this method more than once is an error.
        
        Parameters
        ----------
        payload : dict
            The 'payload' portion of the 'reply' operation associated
            with this async reply instance.

        """
        if self._cancelled:
            if self._pending:
                self._pending = False
            return
        if not self._pending:
            raise RuntimeError("AsyncReply already finished")
        self._pending = False
        self._payload = payload
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
        """ Returns the results portion of the reply.

        If the results of the reply are not yet available due to the
        operation being cancelled or still pending, then this method 
        will raise a ValueError. Otherwise, this method will return 
        the 'results' portion of the 'payload' for the 'reply'.

        Returns
        -------
        result : dict or None
            A dict of results for the reply, or None if an error
            occured during processing.

        """
        if self._pending or self._cancelled:
            raise ValueError('Results not available')
        return self._payload['results']

    def error(self):
        """ Returns the error portion of the reply.

        If the error for the reply is not yet available due to the
        operation being cancelled or still pending, then this method 
        will raise a ValueError. Otherwise, this method will return 
        the 'error' portion of the 'payload' for the 'reply'.

        Returns
        -------
        result : dict or None
            A dict of error information for the reply, or None if no
            error occured during processing.

        """
        if self._pending or self._cancelled:
            raise ValueError('Error not available')
        return self._payload['error']

    def set_callback(self, callback, *args, **kwargs):
        """ Set the callback to be run when the request has finished.

        If the message has already finished and was not cancelled, then
        the callback will be invoked immediately with the results. If 
        the message has been cancelled, this method is a no-op. In all
        cases, this callback will not be called if the reply contains
        an error.

        The callback must accept at least one arguments which is the
        'results' portion of the 'payload' of the reply.

        Parameters
        ----------
        callback : callable
            A callable which accepts at least one argument which will 
            be the results of the operation.

        *args, **kwargs
            Any addional positional or keyword parameters to pass to 
            the callback when it is invoked.

        """
        if self._cancelled:
            return
        self._callback = (callback, args, kwargs)
        if not self._pending:
            self._dispatch()

    def set_errback(self, callback, *args, **kwargs):
        """ Set the callback to be run when the request has finished
        with the error state set.

        If the message has already finished and was not cancelled, then
        the callback will be invoked immediately with the error. If 
        the message has been cancelled, this method is a no-op. In all
        cases, this callback will only be called if the reply contains
        an error.

        The callback must accept at least one arguments which is the
        'error' portion of the 'payload' of the reply.

        Parameters
        ----------
        callback : callable
            A callable which accepts at least one argument which will 
            be the error state of the operation.

        *args, **kwargs
            Any addional positional or keyword parameters to pass to 
            the callback when it is invoked.

        """
        if self._cancelled:
            return
        self._errback = (callback, args, kwargs)
        if not self._pending:
            self._dispatch()

