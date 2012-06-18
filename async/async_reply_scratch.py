#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class AsyncCommandReply(object):
    """ A stub out of a possible api for an async reply object.

    """
    def __init__(self):
        """ Initialize the reply

        """
        self._pending = True
        self._callback = None
        self._results = None
        
    def cancel(self):
        """ Cancel the pending task. The behavior of cancelling is 
        implementation dependent, but at a minimum, the reply will
        never execute a registered callback, or make results available.
        Cancelling a task after it is already completed is a no-op.

        """
        self._pending = False

    def pending(self):
        """ Returns whether or not the async command is still pending
        execution.

        """
        return self._pending

    def results(self):
        """ Returns the results of the async command, or raises a 
        ValueError if the results are not yet available.

        """
        if self._pending:
            raise ValueError("Results not yet available.")
        else:
            return self._results

    def _get_callback(self):
        return self._callback

    def _set_callback(self, cb):
        self._callback = cb

    callback = property(_get_callback, _set_callback)

    # A property which gets/sets a callback to be called when the 
    # results of the command are available
    def finished(self, result):
        """ Called by the application object when the object executing
        the command has finished. The argument will be the result
        of the command handler.

        """
        # store the results and call a registered callback
        self._results = result
        self._pending = False
        self.callback()
