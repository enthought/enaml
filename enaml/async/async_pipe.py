#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class AsyncSendPipe(object):
    """ An abstract base class which defines the interface for a pipe
    used to send messages to a client.

    This is an abstract class so that applications have freedom in
    defining their communication protocols and identification schemas.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def put(self, msg, ctxt):
        """ Put a message on a queue to be handled by the client 
        object.
        
        Parameters
        ----------
        msg : string
            The message to be sent to the client object.
            
        ctxt : dict
            The argument context for the message.

        Returns
        -------
        result : AsyncReply
            An asynchronous reply object for the given message. When
            the client object has finished processing the message, 
            this async reply will notify any registered callbacks.

        """
        raise NotImplementedError


class AsyncRecvPipe(object):
    """ An abstract base class which defines the interface for a pipe
    used to receive messages sent by one messenger to another.

    This is an abstract class to that applications have freedom in 
    defining their communication protocols and identification schemas.

    """
    __metaclass__ = ABCMeta

    def set_callback(self, callback):
        """ Supply a callback to be called when a message becomes 
        available.

        Parameters
        ----------
        callback : callable
            The callable to be invoked when a message is available
            for receiving. It will be passed two arguments: the
            string message name, and the dictionary message context.
            The return value of the callback is the return value
            for the message.

        """
        raise NotImplementedError

