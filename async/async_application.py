#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class AsyncApplicationError(RuntimeError):
    """ A custom RuntimeError for errors relating to the global async
    application instance.

    """
    pass


class AbstractBuilder(object):
    """ An abstract base class which defines the interface for an
    application-specific object charge with building the client
    side ui components.

    """
    @abstractmethod
    def build(self, info):
        """ Build the client-side ui tree from the provided info.

        XXX need to be more specific about what is in this dict.

        This method should block until the client-side UI is built.

        Parameters
        ----------
        info : dict
            The ui tree info dict.

        Returns
        -------
        result : bool
            True if the client ui was built successfully, False
            otherwise.

        """
        raise NotImplementedError


class AsyncApplication(object):
    """ The base class for all asynchronous applications in Enaml.

    This class defines the abstract api which must be implemented by
    concrete subclasses. It also provides the global application 
    instance handling logic.

    """
    __metaclass__ = ABCMeta

    #: The singleton async application instance.
    _instance_ = None

    @staticmethod
    def instance():
        """ Returns the singleton async application instance, or None
        if an application has not yet been created.

        """
        return AsyncApplication._instance_

    def __new__(cls, *args, **kwargs):
        """ Create a new AsyncApplication instance.

        If an application already exists, this will raise an 
        ApplicationError.

        """
        if AsyncApplication._instance_ is not None:
            msg = "The AsyncApplication instance already exists."
            raise AsyncApplicationError(msg)
        instance = super(AsyncApplication, cls).__new__(cls, *args, **kwargs)
        AsyncApplication._instance_ = instance
        return instance

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractmethod
    def register(self, messenger, id_setter):
        """ Registers an AsyncMessenger instance with the application.

        All AsyncMessenger instances will call this method once, when 
        they are created. The application must provide a unique string
        identifier for the messenger by calling the provided 'id_setter' 
        function with a single string argument. This id will be used for 
        all future message passing between this messenger and its client.

        Parameters
        ----------
        messenger : AsyncMessenger
            The async messenger instance for which the application must
            provide a unique identifier.

        id_setter : callable
            A callable which takes one argument which is the unique
            string identifier to assign for this messenger.

        """
        raise NotImplementedError

    @abstractmethod
    def send_message(self, msg_id, msg, ctxt):
        """ Send a message to the client of the given messaging id.

        This method asynchronously delivers messages to the client of 
        the given messaging id. The messaging id is the same as that 
        provided by the application when a messenger was registered. 
        The mechanism by which messages are delivered is dependent
        upon the implementation. The only requirement is that this 
        method must not block while delivering the message.

        Parameters
        ----------
        msg_id : string
            The messaging id to use to route the message to the proper
            client object.

        msg : string
            The message to deliver to the client object.
            
        ctxt : dict
            The message context to deliver with the message.

        Returns
        -------
        result : AsyncReply
            An asynchronous reply object for the given message. This
            async reply object will be notified by the application 
            when the client has finished handling the message.

        """
        raise NotImplementedError

    @abstractmethod
    def builder(self):
        """ Returns and AbstractBuilder object used to build the 
        client-side ui.

        """
        raise NotImplementedError

