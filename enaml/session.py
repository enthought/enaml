#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from uuid import uuid4


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

    def __init__(self, push_handler, username, session_id=None, kwargs=None):
        """ Initialize a Session.

        This should not normally be overridden by users. Instead,
        override the `on_open(...)` method in a subclass.

        Parameters
        ----------
        push_handler : BasePushHandler
            The push handler to use when sending messages from a server
            widget back to the client.

        username : str
            The username associated with this session.

        session_id : str, optional
            The unique session id for this session. If not provided,
            a new one will be created with a uuid.

        kwargs : dict, optional
            The dict of keyword arguments to pass to the on_open()
            method. These arguments will have been provided by the
            user as an item in the handler tuple given to the 
            Application instance.

        """
        self._push_handler = push_handler
        self._username = username
        self._session_id = session_id or uuid4().hex
        self._kwargs = kwargs or {}
        self._session_view = None
        
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
    def session_view(self):
        """ The Enaml view being managed by this session.

        Returns
        -------
        result : view
            The Enaml view for the session, or None if it has not yet
            been created.

        """
        return self._session_view

    def send(self, message):
        """ Send an unsolicited message to the client of this session. 

        Parameters
        ----------
        message : Message 
            The message object to send to the client. The session
            id and username in the header will be filled in by
            the session.

        """
        header = message.header
        header.session = self._session_id
        header.username = self._username
        self._push_handler.push_message(message)

    def on_close(self):
        """ Called by the application when the session is destroyed.

        Use this method to perform any resource cleanup required before
        the session is released by the application. After this method 
        returns, the session should be considered invalid. This method
        is only called once during the session lifetime. 

        """
        pass

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def do_open(self):
        """ Called by the application when the session is opened.

        """
        view = self.on_open(**self._kwargs)
        self._session_view = view

    def do_close(self):
        """ Called by the application when the session is closed.

        """
        self.on_close()
        self._session_view = None

    def handle_request(self, request):
        """ A method called by the application when the client sends
        a request to the session.

        Parameters
        ----------
        request : BaseRequest
            The request object generated by the client.

        """
        msg_type = request.message.header.msg_type
        handler_name = '_on_' + msg_type
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(request)
        else:
            request.reply('error', 'Unhandled message type')

    #--------------------------------------------------------------------------
    # Request Handlers
    #--------------------------------------------------------------------------
    def _on_enaml_snapshot(self, request):
        snapshot = self.session_view.snapshot()
        request.reply(snapshot=snapshot)

