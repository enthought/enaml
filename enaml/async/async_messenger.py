#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty


class AsyncMessenger(object):
    """ An abstract base class which defines the interface of an async
    messenger.

    The interface of an async messenger is deliberately vague to allow
    maximum flexibility for implementations. The interface defined here
    is only that which is required for a messenger which will register
    itelf with an AsyncApplication and may, at some point, be published
    to a client.

    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def target_id(self):
        """ A property which should be write once and then read only. 

        The target id will be a string and will be set by the async 
        application when the messenger is registered. The target id
        should be set before the async pipe since the setter for the
        pipe property may depend on the existence of the target it.

        """
        raise NotImplementedError

    @abstractproperty
    def async_pipe(self):
        """ A property which should be write once and the read only.

        The async pipe will be an instance of AsyncPipe and will be
        set by the async application when the messenger is registered.
        This is the pipe that should be used by the messenger for 
        communication with the client.

        """
        raise NotImplementedError

    @abstractmethod
    def creation_payload(self):
        """ Returns the payload dict for the 'create' action for the
        messenger.

        The contents of this must contain the keys 'action', 'type',
        'parent_id', and 'attributes'. The value of 'action' must be
        the string 'create'. The value of 'type' should be a string
        indicating the type of object to be created by the client.
        The value of 'parent_id' should be a string which is the 
        target id of the parent, or None if the messenger has no
        parent. The value of 'attributes' should be a dictionary 
        of initial attributes to provide to the client.

        Returns
        -------
        results : dict
            A dict which is json serializable and contains the payload
            needed to create a client of the appropriate type.

        """
        raise NotImplementedError

