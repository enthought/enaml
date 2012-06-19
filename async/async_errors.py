#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class AsyncApplicationError(RuntimeError):
    """ A custom RuntimeError for errors relating to the global async
    application instance.

    """
    pass


class AsyncFailure(Exception):
    """ A base class of errors in the context of async execution.

    """
    pass


class CommandFailure(AsyncFailure):
    """ An AsyncFailure representing the failure of a command during its
    execution on a client.

    """
    def __init__(self, messenger_id, cmd, context, message):
        """ Initialize a CommandFailure.

        Parameters
        ----------
        messenger_id : object
            The identifier of the messenger object which originally
            sent the command.

        cmd : string
            The command name which failed execution on the client.

        context : dict
            The context dictionary for the failed command.

        message : string
            A message indicating the nature of the failure on the
            client.

        """
        super(CommandFailure, self).__init__(message)
        self.messenger_id = messenger_id
        self.cmd = cmd
        self.context = context


class CallbackFailure(AsyncFailure):
    """ An AsyncFailure representing the failure of a callback run from
    an AsyncCommand instance.

    """
    def __init__(self, exc_type, exc_value, traceback):
        """ Initialize a CallbackFailure.

        The arguments to this constructor are the same as those returned
        by sys.exc_info().

        Parameters
        ----------
        exc_type : type
            The exception type raised by the callback.

        exc_value : Exception
            The exception instance raised by the callback.

        traceback : traceback
            The traceback instance for the exception location.

        """
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.traceback = traceback

