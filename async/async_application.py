#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from async_errors import AsyncApplicationError


class AsyncApplication(object):
    """ The base class for all asynchronous applications in Enaml.

    This class defines the abstract api which must be implemented by
    concrete subclasses. It also provides the application instance
    handling logic.

    """
    __metaclass__ = ABCMeta

    #: The singleton async application instance.
    _instance_ = None

    @classmethod
    def instance(cls):
        """ Returns the singleton async application instance, or None
        if an application has not yet been created.

        """
        return cls._instance_

    def __new__(cls, *args, **kwargs):
        """ Create a new AsyncApplication instance.

        If an application already exists, this will raise an 
        ApplicationError.

        """
        if cls._instance_ is not None:
            msg = "The AsyncApplication instance already exists."
            raise AsyncApplicationError(msg)
        instance = super(AsyncApplication, cls).__new__(cls, *args, **kwargs)
        cls._instance_ = instance
        return instance

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractmethod
    def register(self, messenger):
        """ Registers the AsyncMessenger instance with the application.

        All AsyncMessenger instances will call this method once, when 
        they are instantiated. The application must provide the messenger 
        with an identifier by assigning to its 'messenger_id' attribute. 
        This id can be any object an application deems necessary, as long 
        as it is provided.

        The application should also perform any other handling that is 
        necessary to initialize message handling for the messenger.

        Parameters
        ----------
        messenger : AsyncMessenger
            The async messenger instance for which the application must
            provide an identifier.

        """
        raise NotImplementedError

    @abstractmethod
    def messenger(self, messenger_id):
        """ Return the messenger object for the given identifier.

        If the messenger does not exist for this application, then
        an AsyncApplicationError should be raised.

        Parameters
        ----------
        messenger_id : object
            The identifier given to a messenger during a previous
            call to 'register(...)'.

        Returns
        -------
        result : AsyncMessenger
            The async messenger for the given identifier.

        """
        raise NotImplementedError

    @abstractmethod
    def send_command(self, messenger, cmd, context):
        """ Send the command to the client of the given messenger.

        This method delivers commands to the clients of AsyncMessenger
        instance. How these messages are delivered is implementation
        dependent, the only requirement is that this must method not
        block while delivering the command.

        Parameters
        ----------
        messenger : AsyncMessenger
            The async messenger instance which is sending the command
            to a client.

        cmd : string
            The command name to be executed by the client.
            
        context : dict
            The argument context for the command.

        Returns
        -------
        result : AsyncCommand
            An asynchronous command object for the given command. This
            async command object will be notified by the application 
            when the client has finished executing the command.

        """
        raise NotImplementedError

