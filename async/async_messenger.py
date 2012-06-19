#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, ReadOnly, Undefined

from async_application import AsyncApplication, ApplicationError


class AsyncMessenger(HasTraits):
    """ The base class of all widgets in Enaml.

    This extends BaseComponent with the concept of sending and receiving
    commands to and from a client widget.

    """
    #: A messenger id is an object provided by the application instance
    #: when an async messenger instance is created and registered. It
    #: allows the application to attach unique meta-info to a messenger 
    #: for any purpose it deems necessary, such as a serializable tag
    #: to send over the network.
    messenger_id = ReadOnly

    def __new__(cls, *args, **kwargs):
        """ Create a new AsyncMessenger instance.

        New instances cannot be created unless and AsyncApplication 
        instance is available.

        """
        app = AsyncApplication.instance()
        if app is None:
            msg = 'An async application instance must be created before '
            msg += 'creating any AsyncMessenger instances.'
            raise ApplicationError(msg)
        instance = super(AsyncMessenger, cls).__new__(cls, args, kwargs)
        app.register(instance)
        if instance.messenger_id is Undefined:
            msg = 'The async application failed to provide an id for '
            msg += 'AsyncMessenger instance.'
            raise ApplicationError(msg)
        return instance

    @property
    def application(self):
        """ Returns the async application instance for use by this
        messenger.

        """
        app = AsyncApplication.instance()
        if app is None:
            msg = 'The async application instance no longer exists.'
            raise ApplicationError(msg)
        return app

    def send(self, cmd, context):
        """ Send a command to another object to be executed
        
        Parameters
        ----------
        cmd : string
            The command to be executed
            
        context : dict
            The argument context for the command

        Returns
        -------
        result : AsyncReply
            An asynchronous reply object for the given command.

        """
        return self.application.send_command(self, cmd, context)
        
    def receive(self, cmd, context):
        """ Handle a command sent by another object.
        
        This method is called by the async application instance when
        there is a command ready to be delivered to this messenger.
        
        This method will dispatch the command to methods defined on a 
        subclass by prefixing the command name with 'receive_'. 

        In order to handle a command named e.g. 'set_label', a sublass 
        should define a method with the name 'receive_set_label' which 
        takes a single argument which is the context dictionary for the 
        command. Exceptions raised in a handler are propagated to the
        application instance.
        
        Parameters
        ----------
        cmd : string
            The command name to be executed.
            
        context : dict
            The argument context for the command.

        Returns
        -------
        result : object or NotImplemented
            The return value of the command handler or NotImplemented
            if this object does not define a handler for the command.

        """
        handler_name = 'receive_' + cmd
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(context)
        return NotImplemented

