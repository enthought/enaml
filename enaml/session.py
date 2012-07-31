#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from enaml.message import Message
from enaml.utils import id_generator


#: The global message id generator for Session objects.
_session_message_id_gen = id_generator('smsg_')


#: The global session id generator for Session objects.
_session_id_gen = id_generator('sid_')


class Session(object):
    """ An object representing the session between a client and an 
    Enaml view.

    The session object is what ensures that each client has their
    own individual instance of a view, so that the only state that
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

    def __init__(self, push_handler, username, kwargs=None):
        """ Initialize a Session.

        This __init__ method should be overridden by users. Instead,
        override the `on_open(...)` method in a subclass.

        Parameters
        ----------
        push_handler : BasePushHandler
            The push handler to use when pushing messages from a server
            widget back to the client.

        username : str
            The username associated with this session.

        kwargs : dict, optional
            The dict of keyword arguments to pass to the on_open()
            method. These arguments will have been provided by the
            user as an item in the handler tuple given to the 
            Application instance.

        """
        self._push_handler = push_handler
        self._username = username
        self._session_id = _session_id_gen.next()
        self._kwargs = kwargs or {}
        self._session_views = []
        self._widgets = {}

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
    def on_open(self, **kwargs):
        """ Called by the application when the session is opened.

        Use this method to initialize any models or state that should
        persist for the duration of the session. This method must also
        create the Enaml view object for the session. This method will
         only be called once during the session lifetime.

        Parameters
        ----------
        **kwargs
            The keyword arguments that were provided as the last
            item in the handler tuple given to the Application.
        
        Returns
        -------
        result : view
            The Enaml component tree comprising the view for this
            session.

        """
        raise NotImplementedError

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
    def session_views(self):
        """ The Enaml views being managed by this session.

        Returns
        -------
        result : list
            The Enaml views for the session.

        """
        return self._session_views

    def send_action(self, widget_id, action, content):
        """ Send an unsolicited message of type 'widget_action' to a
        client widget of this session. 

        This method is normally only called by the MessengerWidget's
        which are owned by this Session object. This should not be
        called directly by user code.
        
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

    def on_close(self):
        """ Called by the application when the session is destroyed.

        Use this method to perform any resource cleanup required before
        the session is released by the application. After this method 
        returns, the session should be considered invalid. This method
        is only called once during the session lifetime. 

        """
        pass

    def open(self):
        """ Called by the application when the session is opened.

        """
        views = self.on_open(**self._kwargs)
        if not isinstance(views, list):
            views = [views]
        self._session_views = views
        for view in views:
            view.set_session(self)

    def close(self):
        """ Called by the application when the session is closed.

        """
        self.on_close()
        self._session_views = []

    def register_widget(self, widget):
        """ A method called by a MessengerWidget when the Session is
        assigned to the widget.

        This allows the Session object to build a mapping of widget
        identifiers to widgets for dispatching messages. This should
        not normally be called by user code.

        Parameters
        ----------
        widget : MessengerWidget
            The widget to which this session was applied.

        """
        self._widgets[widget.widget_id] = widget

    def handle_request(self, request):
        """ A method called by the application when the client sends
        a request to the session.

        This method should not normally be called by user code.

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

