#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from async_application import AsyncApplication, AsyncApplicationError


class AsyncMessenger(object):
    """ A base class which provides the messaging interface between 
    this object and a client object that lives elsewhere.

    This class ensures that objects are registered with the application
    instance when they are instantiated. It also provides 'send' and
    'receive' methods to facilitate message passing between the
    instance and its client.

    The correspondence between the messenger instance and the client
    object is 1:1.

    """
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
        instance.__msg_id = None

        def id_setter(msg_id):
            if not isinstance(msg_id, str):
                msg = 'A messaging id must be a string. Got object of '
                msg += 'type %s instead' % type(msg_id)
                raise TypeError(msg)
            instance.__msg_id = msg_id

        app.register(instance, id_setter)

        if instance.__msg_id is None:
            msg = 'The async application failed to provide a messaging id'
            msg += 'for the AsyncMessenger instance.'
            raise AsyncApplicationError(msg)

        return instance

    @property
    def msg_id(self):
        """ Returns the messaging id string given to this messenger by 
        the application.

        """
        return self.__msg_id

    @property
    def app(self):
        """ Returns the async application instance for use by this
        messenger.

        """
        app = AsyncApplication.instance()
        if app is None:
            msg = 'The async application instance no longer exists.'
            raise AsyncApplicationError(msg)
        return app

    def send(self, msg, ctxt):
        """ Send a message to be handled by a client object.
        
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
        return self.app.send_message(self.msg_id, msg, ctxt)
        
    def recv(self, msg, ctxt):
        """ Handle a message sent by the client object.
        
        This method is called by the async application instance when
        there is a message from the client ready to be delivered to 
        this messenger.
        
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
        handler_name = 'receive_' + msg
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(ctxt)
        return NotImplemented

