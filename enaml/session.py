#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import Iterable
import logging

from traits.api import HasTraits, Instance, Property, List, Str

from enaml.core.object import Object
from enaml.socket_interface import ActionSocketInterface


logger = logging.getLogger(__name__)


class Session(HasTraits):
    """ An object representing the session between a client and its
    Enaml objects.

    The session object is what ensures that each client has their own
    individual instances of objects, so that the only state that is
    shared between clients is that which is explicitly provided by the
    developer.

    """
    #: The string identifier for this session. This is provided by
    #: the application in the `open` method.
    session_id = Property(fget=lambda self: self._session_id)

    #: The socket used by this session for communication. This is
    #: provided by the Application in the `open` method.
    socket = Property(fget=lambda self: self._socket)

    #: The objects being managed by this session. These are updated
    #: during the call to the `open` method.
    objects = Property(fget=lambda self: self._objects)

    #: The user groups to which this session belongs. This should be
    #: set by the user *before* the `on_open` method is called.
    user_groups = List(Str, ['users'])

    #: Internal storage fo the session id.
    _session_id = Str

    #: Internal storage for the session socket
    _socket = Instance(ActionSocketInterface)

    #: Internal storage for the session objects
    _objects = List(Object)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def on_open(self):
        """ Called by the application when the session is opened.

        This method must be implemented in a subclass and is called to
        create the Enaml objects for the session. This method will only
        be called once during the session lifetime.

        Returns
        -------
        result : iterable
            An iterable of Enaml objects for this session.

        """
        raise NotImplementedError

    def on_close(self):
        """ Called by the application when the session is closed.

        This method may be optionally implemented by subclasses so that
        they can perform custom cleaup. After this method returns, the
        session should be considered invalid. This method is only called
        once during the session lifetime.

        """
        pass

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self, session_id, socket):
        """ Called by the application when the session is opened.

        This method will call the `on_open` abstract method which must
        be implemented by subclasses. The method should never be called
        by user code.

        Parameters
        ----------
        session_id : str
            The identifier to use for this session.

        socket : ActionSocketInterface
            A concrete implementation of ActionSocketInterface to use
            for messaging by this session.

        """
        self._session_id = session_id
        objs = self.on_open()
        if not isinstance(objs, Iterable):
            objs = [objs]
        else:
            objs = list(objs)
        self._objects = objs
        for obj in objs:
            obj.session = self
            obj.initialize()
        self._socket = socket
        socket.on_message(self.on_message)

    def close(self):
        """ Called by the application when the session is closed.

        This method will call the `on_close` method which may be
        implemented by subclasses. The method should never be called
        by user code.

        """
        self.on_close()
        for obj in self._objects:
            obj.destroy()
        self._objects = []
        socket = self._socket
        if socket is not None:
            socket.on_message(None)

    def snapshot(self):
        """ Get a snapshot of this session.

        Returns
        -------
        result : list
            A list of snapshot dictionaries representing the current
            state of this session.

        """
        return [obj.snapshot() for obj in self._objects]

    def send(self, object_id, action, content):
        """ Send a message to a client object.

        This method is called by the `Object` instances owned by this
        session to send messages to their client implementations.

        Parameters
        ----------
        object_id : str
            The object id of the client object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        socket = self._socket
        if socket is not None:
            socket.send(object_id, action, content)

    def on_message(self, object_id, action, content):
        """ Receive a message sent to an object owned by this session.

        This is a handler method registered as the callback for the
        action socket. The message will be routed to the appropriate
        `Object` instance.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        obj = Object.lookup_object(object_id)
        if obj is None:
            msg = "Invalid object id sent to Session: %s:%s"
            logger.warn(msg % (object_id, action))
            return
        obj.handle_action(action, content)

