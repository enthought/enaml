#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class AsyncPipe(object):
    """ An abstract base class which defines the interface for a pipe
    used to communicate with a target.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def put_message(self, target_id, payload):
        """ Place a message payload on a queue to be delivered to the
        target.

        Parameters
        ----------
        target_id : str
            The target id string which identifies the peer which 
            should receive the message.

        payload : dict
            A dictionary representing the 'payload' portion of a
            'operation' of type 'message' in the Enaml messaging 
            protocol.

        """
        raise NotImplementedError

    @abstractmethod
    def put_request(self, target_id, payload):
        """ Place a request payload on a queue to be delivered to the
        target.

        Parameters
        ----------
        target_id : str
            The target id string which identifies the peer which 
            should receive the request.

        payload : dict
            A dictionary representing the 'payload' portion of a
            'operation' of type 'request' in the Enaml messaging 
            protocol.

        Returns
        -------
        result : AsyncReply
            An instance of AsyncReply which will be notified with the 
            results of the request once the target has sent back the
            'reply'.

        """
        raise NotImplementedError

    def set_message_callback(self, target_id, callback):
        """ Supply a callback to be called when an operation of type
        'message' is sent by a peer.

        Parameters
        ----------
        target_id : str
            The target id string identifies which messages should be
            received by the callback.

        callback : callable
            A callable which will be invoked when an operation of type 
            'message' is sent by a peer. The callback will be passed a 
            dictionary which represents the 'payload' portion of the
            'operation' object in the Enaml messaging protocol. The
            return value of the callable will be ignored. Exceptions
            raised by the callable will not be sent back to the peer.
            Only a weak reference is maintained to the callback, so 
            the user should craft a callable object of an appropriate
            lifetime.

        """
        raise NotImplementedError

    def set_request_callback(self, target_id, callback):
        """ Supply a callback to be called when an operation of type
        'request' is sent by a peer.

        Parameters
        ----------
        target_id : str
            The target id string identifies which messages should be
            received by the callback.

        callback : callable
            A callable which will be invoked when an operation of type 
            'request' is sent by a peer. The callback will be passed a 
            dictionary which represents the 'payload' portion of the
            'operation' object in the Enaml messaging protocol. The
            return value of the callable should be a dictionary and
            will used as the 'results' portion of the 'payload' for the
            'reply' operation send back to the peer. Exceptions raised 
            by the callable will be used as the 'error' portion of the
            'payload' for the 'reply' operation and sent back to the 
            peer. Only a weak reference is maintained to the callback,
            so the user should craft a callable object of an appropriate
            lifetime.

        """
        raise NotImplementedError

