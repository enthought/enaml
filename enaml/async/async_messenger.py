#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasStrictTraits, Instance, Str

from .async_application import AsyncApplication, AsyncApplicationError
from .async_pipe import AsyncSendPipe, AsyncRecvPipe
from .messenger_mixin import MessengerMixin


class AsyncMessenger(HasStrictTraits, MessengerMixin):
    """ A base class which provides the messaging interface between 
    this object and a client object that lives elsewhere.

    This class ensures that objects are registered with the application
    instance when they are instantiated. It also provides 'send' and
    'receive' methods to facilitate message passing between the
    instance and its client.

    The correspondence between the messenger instance and the client
    object is 1:1.

    """
    #: The target id to use when sending messages across the pipes.
    #: This will be supplied by the applicaiton when the messenger
    #: registers itself. It should not be modified by the user code.
    target_id = Str

    #: The messaging send pipe. This will be supplied by the application
    #: when the messenger registers itself. It should not be modified
    #: by the user code.
    send_pipe = Instance(AsyncSendPipe)

    #: The messaging recv pipe. This will be supplied by the application
    #: then the messenger registers itself. It should not be modified
    #: by the user code.
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
        target_id, send_pipe, recv_pipe = app.register(instance)

        instance.target_id = target_id
        instance.send_pipe = send_pipe
        instance.recv_pipe = recv_pipe

        return instance

