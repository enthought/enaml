#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class MessengerMixin(object):
    """ A mixin class which provides some convenience methods for
    sending and receiving messages across async pipes.

    This mixin expects that it is included in a class heierarchy 
    which contains an instance of AsyncMessenger.

    """
    def send_message(self, payload):
        """ Send a message to be handled by the target object.
        
        Parameters
        ----------
        payload : dict
            A dictionary representing the 'payload' portion of a
            'operation' of type 'message' in the Enaml messaging 
            protocol.

        """
        self.async_pipe.put_message(self.target_id, payload)
        
    def send_request(self, payload):
        """ Send a request to be handled by the target object.

        Parameters
        ----------
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
        return self.async_pipe.put_request(self.target_id, payload)

    def recv_message(self, payload):
        """ Handle a message sent by the client object.
        
        This method is called by the recv pipe when there is a message 
        operation from the target ready to be handled.
        
        This method will dynamically route the payload of the the 
        message to handler methods defined on the object by mangling
        the 'action' of the payload according to a schema.

        The prefix of a message handler is 'on_message_'. The suffix of
        the handler is the name of the action with hyphens replaced by 
        underscores. As an example, in order to handle a message action
        named 'set-label', a subclass should define a method named 
        'on_message_set_label' which accepts a single argument which is
        the payload dict for the operation.
        
        Any return value from a handler is ignored since message actions
        in the Enaml messaging protocol do not require responses.

        Parameters
        ----------
        payload : dict
            A dictionary representing the 'payload' portion of a
            'operation' of type 'message' in the Enaml messaging 
            protocol.

        """
        handler_name = 'on_message_' + payload['action'].replace('-', '_')
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(payload)
            return
        # XXX log handler misses?
            
    def recv_request(self, payload):
        """ Handle a request sent by the client object.
        
        This method is called by the recv pipe when there is a request 
        operation from the target ready to be handled.
        
        This method will dynamically route the payload of the the 
        request to handler methods defined on the object by mangling
        the 'action' of the payload according to a schema.

        The prefix of a request handler is 'on_request_'. The suffix of
        the handler is the name of the action with hyphens replaced by 
        underscores. As an example, in order to handle a request action
        named 'get-data', a subclass should define a method named 
        'on_request_get_data' which accepts a single argument which is
        the payload dict for the operation.
        
        The return value should be a dict which will be used as the 
        'results' value in the payload of the 'reply' operation which
        is sent back to the requester.

        If no handler is found for the request, this method will raise
        a NotImplementedError.

        Parameters
        ----------
        payload : dict
            A dictionary representing the 'payload' portion of a
            'operation' of type 'request' in the Enaml messaging 
            protocol.

        Returns
        -------
        results : dict
            The dictionary of result values returned by the handler to
            use as the 'results' value in the payload of the 'reply'. 

        Raises
        ------
        NotImplementedError
            This exception will be raised if no handler is found for 
            the given request action.

        """
        handler_name = 'on_request_' + payload['action'].replace('-', '_')
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(payload)        
        msg = 'No handler found for request action %s' % payload['action']
        raise NotImplementedError(msg)

