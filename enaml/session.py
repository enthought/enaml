#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import Iterable

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
        'widget_action': '_dispatch_widget_message',
        'widget_action_response': '_dispatch_widget_message',
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
        self._session_views = []
        self._widgets = {}
        self.init(*args, **kwargs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def _on_message_snapshot(self, request):
        """ Handle the 'snapshot' message type.

        This handler will create the list of snapshot objects for the
        current views being managed by the session and send an a
        response to the client.

        Parameters
        ----------
        request : BaseRequest
            The request object containing the message sent by client.

        """
        snapshot = [view.snapshot() for view in self._session_views]
        content = {'snapshot': snapshot}
        request.send_ok_response(content=content)

    def _dispatch_widget_message(self, request):
        """ Route a 'widget_action' message to the target widget.

        This handler will lookup the widget using the given widget
        id and pass the action and message content to the action
        handler on the widget. If the widget does not exist, then
        an error response will be sent to the client.

        TODO - handle the "widget_action_response" message type.
        
        Parameters
        ----------
        request : BaseRequest
            The request object containing the message sent by client.

        """
        message = request.message
        if message.header.msg_type == 'widget_action':
            widget_id = message.metadata.widget_id
            if widget_id not in self._widgets:
                request.send_error_response('Invalid widget id')
                return
            widget = self._widgets[widget_id]
            widget.handle_action(message.metadata.action, message.content)
            request.send_ok_response()
        # XXX handle msg_type 'widget_action_response'

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractmethod
    def on_open(self):
        """ Called by the application when the session is opened.

        This method must be implemented in a subclass and is used to 
        create the Enaml view objects for the session. This method will
        only be called once during the session lifetime.
        
        Returns
        -------
        result : iterable
            An iterable of Enaml component trees which are the views
            for this session. 

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
        *args, **kwargs
            The positional and keyword arguments that were provided
            by the user to the SessionFactory which created this 
            session.

        """
        pass

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @classmethod
    def factory(cls, sess_name=None, sess_descr=None, *args, **kwargs):
        """ A utility classmethod that returns a SessionFactory.
        
        If the name or description are not given, they will be inferred
        by looking for class attributes `name` and `description`. If 
        these do not exist, then the class name and docstring will be 
        used. If more control is needed, then the SessionFactory should 
        be manually created.

        Parameters
        ----------
        sess_name : str, optional
            A unique, human friendly name for the session.
        
        sess_descr : str, optional
            A brief description of the session.
        
        *args, **kwargs
            Optional postional and keyword arguments to pass to the
            Session's `init` method when it's created.
        
        """
        from .session_factory import SessionFactory
        if sess_name is None:
            sess_name = getattr(cls, 'name', cls.__name__)
        if sess_descr is None:
            sess_descr = getattr(cls, 'description', cls.__doc__)
            if sess_descr is None:
                msg = ('Session class must have a `description` class '
                       'attribute or a docstring to use the `factory` '
                       'classmethod. ')
                raise AttributeError(msg)
        factory = SessionFactory(sess_name, sess_descr, cls, *args, **kwargs)
        return factory

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
    def session_views(self):
        """ The Enaml views being managed by this session.

        Returns
        -------
        result : tuple
            The Enaml views in use for the session.

        """
        return self._session_views
    
    def send_action(self, widget_id, action, content):
        """ Send an unsolicited message of type 'widget_action' to a
        client widget of this session. 

        This method is called by the MessengerWidget's which are owned 
        by this Session object. This should never be called directly by 
        user code.
        
        Parameters
        ----------
        widget_id : str
            The widget identifier for the widget sending the message.

        action : str
            The action to be performed by the client widget.

        content : dict
            The content dictionary for the action.

        """
        header = {
            'session': self._session_id,
            'username': self._username,
            'msg_type': 'widget_action',
            'msg_id': _session_message_id_gen.next()
        }
        metadata = {'widget_id': widget_id, 'action': action}
        message = Message((header, {}, metadata, content))
        self._push_handler.push_message(message)

    def send_children_changed(self, widget_id, content):
        """ Send an unsolicited 'widget_children_changed' message to
        the client of this session.

        This method is called by the MessengerWidget's which are owned 
        by this Session object. This should never be called directly by 
        user code.
        
        Parameters
        ----------
        widget_id : str
            The widget identifier for the widget sending the message.

        content : dict
            The content dictionary for the action.

        """
        header = {
            'session': self._session_id,
            'username': self._username,
            'msg_type': 'widget_children_changed',
            'msg_id': _session_message_id_gen.next()
        }
        metadata = {'widget_id': widget_id}
        message = Message((header, {}, metadata, content))
        self._push_handler.push_message(message)

    def open(self):
        """ Called by the application when the session is opened.

        This method should never be called by user code.
        
        """
        views = self.on_open()
        if not isinstance(views, Iterable):
            views = (views,)
        else:
            views = tuple(views)
        self._session_views = views
        for view in views:
            view.set_session(self)

    def close(self):
        """ Called by the application when the session is closed.

        """
        self.on_close()
        # XXX need to do explicit view destruction?
        self._session_views = ()

    def register_widget(self, widget):
        """ A method called by a MessengerWidget when the Session is
        assigned to the widget.

        This allows the Session object to build a mapping of widget
        identifiers to widgets for dispatching messages. This method
        should never be called by user code.

        Parameters
        ----------
        widget : MessengerWidget
            The widget to which this session was applied.

        """
        self._widgets[widget.widget_id] = widget

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

