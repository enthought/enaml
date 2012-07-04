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
    def register(self, messenger):
        """ Registers an AsyncMessenger instance with the application.

        The application should supply an appropriate target_id and
        async_pipe to the messenger by assigning to those properties.

        Parameters
        ----------
        messenger : AsyncMessenger
            The async messenger instance for which the application 
            must provide a unique target id and communication pipe.
            The target id must be assigned to the messenger *before*
            the async pipe.

        """
        raise NotImplementedError

    @abstractmethod
    def publish(self, targets):
        """ Make previously registered messengers available on the 
        client.

        The semantics of 'publish' are implementation defined. At a
        minimum, publishing a messenger will make it available on 
        the client for communication. Targets will be published on
        the client in the order in which their target ids are 
        provided.

        Parameters
        ----------
        targets : iterable
            An iterable which yields the target ids for previously 
            registered AsyncMessenger instances. If any of the target
            ids do not exist, or were not registered, a ValueError will
            be raised and nothing will be transmitted to the client.

        """
        raise NotImplementedError

    @abstractmethod
    def destroy(self, targets):
        """ Destroy previously registered messengers. If the messenger
        has been published, it will be effecitvely unpublished.

        Parameters
        ----------
        targets : iterable
            An iterable which yields the target ids for previously 
            registered AsyncMessenger instances. If any of the target
            ids do not exist, or were not registered, that id will
            be skipped.

        """
        raise NotImplementedError

    @abstractmethod
    def mainloop(self):
        """ Enter the mainloop of the application.

        This is a blocking call which starts and enters the main event 
        loop of the application. The event loop can be explicitly ended
        by calling the 'exit' method. Implicit termination of the event
        loop is allowed, but is implementation defined. 

        """
        raise NotImplementedError

    @abstractmethod
    def exit(self):
        """ Exit the mainloop of the application.

        Calling this method will cause a previous blocking call to
        'mainloop' to unblock and return. If the mainloop is not 
        running, then this is a no-op.

        """
        raise NotImplementedError

