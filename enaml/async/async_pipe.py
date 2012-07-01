#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class AsyncSendPipe(object):
    """ An abstract base class which defines the interface for a pipe
    used to send operations to a target.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def put(self, operation):
        """ Put an operation on a queue to be handled by a target.
        
        Parameters
        ----------
        msg : string
            The message to be sent to the client object.
            
        operation : dict
            An operation conforming to the Enaml messaging protocol.

        Returns
        -------
        result : AsyncReply or None
            If the 'type' of the operation is 'request', then an 
            asynchronous reply object will be returned. This object
            will be notified with the reply for the request once the
            target has finished processing. If the operation type is
            'message' or 'reply', then None will be returned.

        """
        raise NotImplementedError


class AsyncRecvPipe(object):
    """ An abstract base class which defines the interface for a pipe
    used to receive operations sent by a peer.

    """
    __metaclass__ = ABCMeta

    def set_callback(self, callback):
        """ Supply a callback to be called when a message becomes 
        available.

        Parameters
        ----------
        callback : callable
            The callable to be invoked when an operation is available
            for receiving. The callback will be passed a dictionary
            which represents an 'operation' object in the Enaml 
            messaging protocol. 

        """
        raise NotImplementedError

