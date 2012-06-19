#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque
import sys


class Failure(object):
    """ A stub out failure class. For now, this just the exception
    info, but may be extended in the future to be more robust.

    """
    def __init__(self, exc_type, exc_value, traceback):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.traceback = traceback


class AsyncCommand(object):
    """ An async command object which notifies on completion.

    An async command is returned by an application instance whenver
    a command is sent to receiver. Since the commands are delivered
    asynchronously, this object is provided so that user code can
    be notified when the command has completed.

    This class is very similar to a twisted Deferred object with the
    key difference that chaining of AsyncCommands is not permitted.

    A user may register callbacks to be executed when the results of
    the command are available by calling the 'add_callback' method.
    When results are available, the first registered callback will
    receive the results of the command. The return value of this 
    callback will be passed to the next callback and so on. 

    Error handlers may be registered via 'add_errback'. If a 
    callback raises and exception during execution, the first
    registered errback is called. This handler may either return
    a valid value, raise a new exception, or return the provided
    failure value. Only the first case stops the propogation of
    the failure.

    XXX - more documentation, for now, if you know how a twisted
          Deferred works, then this class will be familiar.

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
        self._dispatching = False
        self._callbacks = deque()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _dispatch_callbacks(self):
        """

        """
        # Guard against recursion
        if self._dispatching:
            return

        last_result = self._results
        callbacks = self._callbacks
        while callbacks:
            if self._cancelled:
                break # break (unlike return) allows for logging of errors
            handler = callbacks.popleft()[isinstance(last_result, Failure)]
            if handler is None:
                continue
            cb, args, kwargs = handler
            try:
                self._dispatching = True
                try:
                    last_result = cb(self, last_result, *args, **kwargs)
                finally:
                    self._dispatching = False
            except Exception:
                last_result = Failure(*sys.exc_info())

        # We processed all of the callbacks and still have a failure
        # result that was unhandled.
        if isinstance(last_result, Failure):
            # probably want to log the failure here, instead of raising
            raise ValueError("Failed dispatching")

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def cancel(self):
        """ Cancel the execution of the command. 

        If the command is no longer pending, then this operation is a
        no-op. Otherwise, the cancel command callback (if provided) 
        will be called, and no further callbacks will be executed.

        """
        if self._pending:
            self._pending = False
            self._cancelled = True
            cancel_cmd = self._cancel_cmd
            if cancel_cmd is not None:
                cancel_cmd(self)

    def finished(self, results):
        """ Called by the application object when the command is finished
        executing.

        Calling this method more than once is a Runtime Error.
        
        Parameters
        ----------
        results : object
            The return value of the commmand that was executed on
            the client.

        """
        if self._cancelled:
            return
        if not self._pending:
            raise RuntimeError("AsyncCommand already finished")
        self._pending = False
        self._results = results
        self._dispatch_callbacks()

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

        If the results of the command are not yet available, due to the
        command being cancelled, or the command is still pending this 
        method will raise a ValueError.

        Returns
        -------
        result : object
            The result of the async command.

        """
        if self._pending or self._cancelled:
            raise ValueError('Results not available')
        return self._results

    def add_callback(self, callback, *args, **kwargs):
        """ Add a callback to the list of callbacks to be run when the
        command has finished.

        If the command has already finished and was not cancelled, then 
        the callback will be executed immediately with the results of
        the previously executed callback.

        The callback must accept at least two arguments: this deferred
        object, and the results of the previous callback. These args
        will be followed by any positional and keyword arguments 
        provided here. 

        The first callback added will receive the results of the 
        command that was executed, which is the same object that
        would be returned by a call to the 'results' method.

        """
        if self._cancelled:
            return
        cbs = ((callback, args, kwargs), None)
        self._callbacks.append(cbs)
        if not self._pending:
            self._dispatch_callbacks()

    def add_errback(self, errback, *args, **kwargs):
        if self._cancelled:
            return
        cbs = (None, (errback, args, kwargs))
        self._callbacks.append(cbs)
        if not self._pending:
            self._dispatch_callbacks()

