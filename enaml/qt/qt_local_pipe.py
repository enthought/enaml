#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import WeakValueDictionary

from enaml.async.async_pipe import AsyncPipe
from enaml.async.async_reply import AsyncReply

from .qt.QtCore import QObject, Signal, Slot


class QtLocalPipe(QObject):
    """ A QObject subclass which implements the async pipe interfaces
    for a local Qt application.

    """
    #: The signal used by the pipe to send operations. This signal 
    #: should be connected to the 'receive_message' slot on the peer 
    #: pipe using Qt.QueuedConnection. This signal can also be connected 
    #: to by external sources to monitor the operations send by the 
    #: application.
    send_operation = Signal(object)

    def __init__(self, op_id_gen):
        """ Initialize a QtLocalPipe.

        Parameters
        ----------
        op_id_gen : generator
            A generator which yields strings which serve as operation
            identifiers for request routing.

        """
        super(QtLocalPipe, self).__init__()
        self._op_id_gen = op_id_gen
        self._msg_callbacks = WeakValueDictionary()
        self._req_callbacks = WeakValueDictionary()
        self._async_replies = {}

    #--------------------------------------------------------------------------
    # Private Api
    #--------------------------------------------------------------------------
    def _cancel_request(self, async_reply):
        """ A private method which is supplied to the generated async
        reply objects so that they may cancel delivery of a message.

        Parameters
        ----------
        async_reply : AsyncReply
            The async reply instance associated with the message to be
            cancelled.

        """
        self._async_replies.pop(async_reply.op_id, None)

    def _dispatch_message(self, operation):
        """ A private method which dispatches a 'message' operation.

        """
        handler = self._msg_callbacks.get(operation['target_id'])
        if handler is not None:
            handler(operation['payload'])
        else:
            # XXX log message handler misses?
            pass
            
    def _dispatch_request(self, operation):
        """ A private method which dispatches a 'request' operation and
        emits an appriate 'reply' operation.

        """
        target_id = operation['target_id']
        handler = self._req_callbacks.get(target_id)
        if handler is not None:
            try:
                results = handler(operation['payload'])
                error = None
            except Exception as exc:
                results = None
                error = {'type': type(exc).__name__, 'message': exc.message}
        else:
            results = None
            msg = 'Target not found'
            error = {'type': 'NotImplementedError', 'message': msg}
        reply_op = {
            'type': 'reply',
            'target_id': target_id,
            'operation_id': operation['operation_id'],
            'payload': {'results': results, 'error': error},
        }
        self.send_operation.emit(reply_op)

    def _dispatch_reply(self, operation):
        """ A private method which dispatches a 'reply' operation.

        """
        reply = self._async_replies.pop(operation['operation_id'], None)
        if reply is not None:
            # XXX log exceptions raised from reply callbacks?
            reply.finished(operation['payload'])
        else:
            # XXX log reply misses? It could have been cancelled and 
            # hence no longer exists...
            pass

    #--------------------------------------------------------------------------
    # Public Slots
    #--------------------------------------------------------------------------
    @Slot(object)
    def receive_operation(self, operation):
        """ A slot which should be connected to the 'send_operation' 
        signal of the peer pipe using a Qt.QueuedConnection. 

        This will dispatch the operation to the appropriate handler and
        send back a 'reply' operation if appropriate.

        """
        handler_name = '_dispatch_' + operation['type']
        handler = getattr(self, handler_name)
        handler(operation)

    #--------------------------------------------------------------------------
    # Async Pipe Interface
    #--------------------------------------------------------------------------
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
        op = {
            'type': 'message',
            'target_id': target_id,
            'operation_id': None,
            'payload': payload,
        }
        self.send_operation.emit(op)

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
        op_id = self._op_id_gen.next()
        op = {
            'type': 'message',
            'target_id': target_id,
            'operation_id': op_id,
            'payload': payload,
        }
        reply = AsyncReply(op_id, self._cancel_request)
        self._async_replies[op_id] = reply
        self.send_operation.emit(op)
        return reply

    def set_message_callback(self, target_id, callback):
        """ Supply a callback to be called when an operation of type
        'message' is sent by the peer.

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
        self._msg_callbacks[target_id] = callback

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
        self._req_callbacks[target_id] = callback


AsyncPipe.register(QtLocalPipe)

