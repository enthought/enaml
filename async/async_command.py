#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from async_errors import CommandFailure


class AsyncCommand(object):
    """ An async command object which notifies on completion.

    An async command is returned by an application instance whenver
    a command is sent to a client. Since the commands are delivered
    asynchronously, this object is provided so that user code can
    be notified when the command has completed or failed.

    A user may register a callback to be executed when the results of 
    the command are available by calling the 'set_callback' method.
    If the command succesfully executes, the callback will be invoked
    with the results of the command.

    A user may also register a failure callback which will be invoked
    if the command fails to execute properly by the client by calling
    the 'set_failback' method.

    """
    def __init__(self, cancel_cmd=None):
        """ Initialize an AsyncCommandReply.

        Parameters
        ----------
        cancel_cmd : callable, optional
            An optional callable that can be provided to cancel a
            command before it has run. The callable should accept a 
            single argument, which will be this async command instance.

        """
        self._cancel_cmd = cancel_cmd
        self._pending = True
        self._cancelled = False
        self._results = None
        self._callback = None
        self._failback = None

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _dispatch(self):
        """ XXX document me

        """
        results = self._results
        if isinstance(results, CommandFailure):
            handler = self._failback
        else:
            handler = self._callback
        if handler is not None:
            cb, args, kwargs = handler
            # XXX handle exceptions in callbacks?
            cb(self._results, *args, **kwargs) 

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def cancel(self):
        """ Cancel the execution of the command. 

        If the command is no longer pending, then this operation is a
        no-op. Otherwise, the cancel command callback (if provided) 
        will be called, and no further dispatching will be performed.

        """
        self._cancelled = True
        if self._pending:
            self._pending = False
            cancel_cmd = self._cancel_cmd
            if cancel_cmd is not None:
                cancel_cmd(self)

    def finished(self, results):
        """ Called by the application object when the command is finished
        executing.

        Calling this method more than once is an error.
        
        Parameters
        ----------
        results : object
            The results of the commmand that was executed on the client
            or a CommandFailure object if the command failed.

        """
        if self._cancelled:
            if self._pending:
                self._pending = False
            return
        if not self._pending:
            raise RuntimeError("AsyncCommand already finished")
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
        """ Set the callback to be run when the command has finished.

        If the command has already finished and was not cancelled, then
        the callback will be invoked immediately with the results. If 
        the command has been cancelled, this method is a no-op.

        The callback must accept at least one arguments which is the
        results of the command.

        If the command fails, then the registered callback will not be
        called. Instead the registered failback will be invoked with 
        a CommandFailure instance.

        Parameters
        ----------
        callback : callable
            A callable which accepts at least one argument which will 
            be the results of the command.

        *args, **kwargs
            Any addional positional or keyword parameters to pass to 
            the callback when it is invoked.

        """
        if self._cancelled:
            return
        self._callback = (callback, args, kwargs)
        if not self._pending:
            self._dispatch()

    def set_failback(self, failback, *args, **kwargs):
        """ Set the callback to be run if the command fails.

        If the command has already failed and was not cancelled, then
        the callback will be invoked immediately with the failure. If 
        the command has been cancelled, this method is a no-op.

        The callback must accept at least one arguments which is an
        instance of CommandFailure.

        If the command succeeds, then the failback will not be called.

        Parameters
        ----------
        callback : callable
            A callable which accepts at least one argument which will 
            be the results of the command.

        *args, **kwargs
            Any addional positional or keyword parameters to pass to 
            the callback when it is invoked.
            
        """
        if self._cancelled:
            return
        self._failback = (failback, args, kwargs)
        if not self._pending:
            self._dispatch()

