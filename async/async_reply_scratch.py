#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class AsyncCommandReply(object):
    """ A stub out of a possible api for an async reply object.

    """
    def cancel(self):
        """ Cancel the pending task. The behavior of cancelling is 
        implementation dependent, but at a minimum, the reply will
        never execute a registered callback, or make results available.
        Cancelling a task after it is already completed is a no-op.

        """
        pass

    def pending(self):
        """ Returns whether or not the async command is still pending
        execution.

        """
        pass


    def results(self):
        """ Returns the results of the async command, or raises a 
        ValueError if the results are not yet available.

        """
        pass

    def _get_callback(self):
        pass

    def _set_callback(self, cb):
        pass

    # A property which gets/sets a callback to be called when the 
    # results of the command are available
    def finished(self, result):
        """ Called by the application object when the object executing
        the command has finished. The argument will be the result
        of the command handler.

        """
        # store the results and call a registered callback
        pass

