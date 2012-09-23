#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import Iterable

from enaml.core.object import Object

from .message import Message
from .utils import id_generator


#: The global message id generator for Session objects.
_session_message_id_gen = id_generator('smsg_')


#: The global session id generator for Session objects.
_session_id_gen = id_generator('sid_')


class Session(object):
    """ An object representing the session between a client and its 
    Enaml views.

    The session object is what ensures that each client has their
    own individual instances of views, so that the only state that
    is shared between clients is that which is explicitly provided
    by the developer.

    The session object is also responsible for manage communication
    between an Enaml widget and the server which is connected to the
    client.

    """
    __metaclass__ = ABCMeta

    #: A message dispatch table used to speed up message routing
    _message_routes = {
        'snapshot': '_on_message_snapshot',
        'object_action': '_dispatch_object_message',
        'object_action_response': '_dispatch_object_message',
    }

    def __init__(self, push_handler, username, args, kwargs):
        """ Initialize a Session.

        The Session class cannot be used directly. It must be subclassed
        and the subclass must implement the `on_open` method. The user
        can also optionally implement the `init` and `on_close` methods.
        This __init__ method should never be overridden.

        Parameters
        ----------
        push_handler : BasePushHandler
            The push handler to use when pushing messages from a server
            widget back to the client.

        username : str
            The username associated with this session.
        
        args : tuple
            Additional arguments passed to the `init` method.
        
        kwargs : tuple
            Additional keyword arguments passed to the `init` method.

        """
        self._push_handler = push_handler
        self._username = username
        self._session_id = _session_id_gen.next()
        self._session_objects = []
        self.init(*args, **kwargs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def _on_message_snapshot(self, request):
        """ Handle the 'snapshot' message type.

        This handler will create a list of snapshots for the current 
        objects being managed by the session and send a repsonse to 
        the client.

        Parameters
        ----------
        request : BaseRequest
            The request object containing the message sent by client.

        """
        snapshot = [obj.snapshot() for obj in self._session_objects]
        content = {'snapshot': snapshot}
        request.send_ok_response(content=content)

    def _dispatch_object_message(self, request):
        """ Route an 'object_action' message to the target object.

        This handler will lookup the object using the given object id 
        and pass the action and message content to the action handler 
        on the object. If the object does not exist, then an error 
        response will be sent to the client.

        TODO - handle the "object_action_response" message type.
        
        Parameters
        ----------
        request : BaseRequest
            The request object containing the message sent by client.

        """
        message = request.message
        if message.header.msg_type == 'object_action':
            object_id = message.metadata.object_id
            obj = Object.lookup_object(object_id)
            if obj is None:
                request.send_error_response('Invalid object id')
                return
            obj.handle_action(message.metadata.action, message.content)
            request.send_ok_response()
        # XXX handle msg_type 'object_action_response'

    def _on_object_action(self, object_id, action, content):
        """ The signal handler for the `action` signal on an Object. 

        This handler is connected to the `action` signal of the objects
        being used by this Session. It converts the action signal into
        a message to the client.
        
        Parameters
        ----------
        object_id : str
            The object identifier for the object emitting the action.

        action : str
            The action to performed by the object.

        content : dict
            The content dictionary for the action.

        """
        header = {
            'session': self._session_id,
            'username': self._username,
            'msg_type': 'object_action',
            'msg_id': _session_message_id_gen.next()
        }
        metadata = {'object_id': object_id, 'action': action}
        message = Message((header, {}, metadata, content))
        self._push_handler.push_message(message)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractmethod
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

    def init(self, *args, **kwargs):
        """ Perform subclass specific initialization.
        
        This method may be optionally implemented by subclasses so that
        they can perform custom initialization with the arguments passed
        to the factory which created the session. This method is called 
        at the end of the `__init__` method.
        
        Parameters
        ----------
        args
            The positional arguments that were provided by the user to 
            the SessionFactory which created this session.

        kwargs
            The keyword arguments that were provided by the user to the
            SessionFactory which created this session.

        """
        pass

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @property
    def session_id(self):
        """ The unique identifier for this session.

        Returns
        -------
        result : str
            A unique identifier string for this session.

        """
        return self._session_id

    @property
    def username(self):
        """ The username associated with this session.

        Returns
        -------
        result : str
            The username for this session.

        """
        return self._username

    @property
    def session_objects(self):
        """ The Enaml objects being managed by this session.

        Returns
        -------
        result : tuple
            The Enaml objects in use for the session.

        """
        return self._session_objects

    def open(self):
        """ Called by the application when the session is opened.

        This method should never be called by user code.
        
        """
        objs = self.on_open()
        if not isinstance(objs, Iterable):
            objs = (objs,)
        else:
            objs = tuple(objs)
        self._session_objects = objs
        handler = self._on_object_action
        for obj in objs:
            obj.initialize()
            for obj in obj.traverse():
                obj.action.connect(handler)

    def close(self):
        """ Called by the application when the session is closed.

        """
        self.on_close()
        # XXX Explicity close the client connection

    def handle_request(self, request):
        """ A method called by the application when the client sends
        a request to the session.

        This method should never be called by user code.

        Parameters
        ----------
        request : BaseRequest
            The request object generated by the client.

        """
        # The application has already verified that the msg_type is a 
        # supported message type of the session. So if this results in
        # a KeyError, then it's a problem with the server.
        msg_type = request.message.header.msg_type
        route = self._message_routes[msg_type]
        getattr(self, route)(request)

