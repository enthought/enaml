#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasStrictTraits, Instance

from enaml.utils import WeakMethodWrapper

from .async_application import AsyncApplication, AsyncApplicationError
from .async_pipe import AsyncSendPipe, AsyncRecvPipe


class AsyncMessenger(HasStrictTraits):
    """ A base class which provides the messaging interface between 
    this object and a client object that lives elsewhere.

    This class ensures that objects are registered with the application
    instance when they are instantiated. It also provides 'send' and
    'receive' methods to facilitate message passing between the
    instance and its client.

    The correspondence between the messenger instance and the client
    object is 1:1.

    """
    #: The messaging send pipe. This will be supplied by the application
    #: when the messenger registers itself.
    send_pipe = Instance(AsyncSendPipe)

    #: The messaging recv pipe. This will be supplied by the application
    #: then the messenger registers itself.
    recv_pipe = Instance(AsyncRecvPipe)

    def __new__(cls, *args, **kwargs):
        """ Create a new AsyncMessenger instance.

        New instances cannot be created unless and AsyncApplication 
        instance is available.

        """
        app = AsyncApplication.instance()
        if app is None:
            msg = 'An async application instance must be created before '
            msg += 'creating any AsyncMessenger instances.'
            raise AsyncApplicationError(msg)
        
        instance = super(AsyncMessenger, cls).__new__(cls, args, kwargs)
        send_pipe, recv_pipe = app.register(instance)

        instance.send_pipe = send_pipe
        instance.recv_pipe = recv_pipe

        callback = WeakMethodWrapper(instance.recv, default=NotImplemented)
        instance.recv_pipe.set_callback(callback)
        
        return instance

    def send(self, ctxt):
        """ Send a message to be handled by a client object.
        
        The message is placed on the send pipe for later delivery to
        the client. The return value is an asynchronous reply object
        which can provide notification when the message is finished.

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
        return self.send_pipe.put(ctxt)
        
    def recv(self, ctxt):
        """ Handle a message sent by the client object.
        
        This method is called by the recv pipe when there is a message 
        from the client ready to be delivered to this messenger.
        
        This method will dispatch the message to methods defined on a 
        subclass by prefixing the command name with 'receive_'. 

        In order to handle a message named e.g. 'set_label', a sublass 
        should define a method with the name 'receive_set_label' which 
        takes a single argument which is the context dictionary for the 
        message. 

        Exceptions raised in a handler are propagated.
        
        Parameters
        ----------
        msg : string
            The message to be handled by the client.
            
        ctxt : dict
            The context dictionary for the message.

        Returns
        -------
        result : object or NotImplemented
            The return value of the message handler or NotImplemented
            if this object does not define a handler for the message.

        """
        handler_name = 'receive_' + ctxt['action']
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(ctxt)
        return NotImplemented

