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

    The lifetime of the created client tree is bound to the lifetime
    of the builder instance. So the consumer of the builder should
    store away a reference to it until the client ui is no longer
    needed.

    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def build(self, info):
        """ Build the client-side ui tree from the provided info.

        XXX need to be more specific about what is in this dict.

        This method should(?) block until the client-side UI is built.

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
    def register(self, messenger):
        """ Registers an AsyncMessenger instance with the application.

        All AsyncMessenger instances will call this method once, when 
        they are created. The application must provide the messaging
        target id and pipes which will be used for communication by 
        this messenger.

        Parameters
        ----------
        messenger : AsyncMessenger
            The async messenger instance for which the application must
            provide a unique identifier.

        Returns
        -------
        result : (target_id, send_pipe, recv_pipe)
            A 3-tuple of target id and pipes to be used by the messenger.
            The target id is a string which will uniquely identify the 
            messenger instance for the application. The first pipe is an 
            instance of async_pipe.AsyncSendPipe and should be used to 
            send operations to the target. The second pipe is an instance
            of async_pipe.AsyncRecvPipe and should be used to receive 
            operations from the target.

        """
        raise NotImplementedError

    @abstractmethod
    def builder(self):
        """ Returns and AbstractBuilder object used to build the 
        client-side ui.

        The lifetime of the created client side ui is tied to the
        lifetime of the builder.

        """
        raise NotImplementedError

