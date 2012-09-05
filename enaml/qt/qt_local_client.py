#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from enaml.message import Message
from enaml.utils import id_generator, log_exceptions

from .qt.QtCore import Qt
from .qt_client_session import QtClientSession


#: The global message id generator the local qt clients
_qtclient_message_id_gen = id_generator('qtcmsg_')


class QtLocalClient(object):
    """ A client for managing server sessions in an in-process Qt
    environment.

    """
    #: A message table to speed up message dispatching
    _message_routes = {
        'start_session_response': '_on_message_start_session_response',
        'end_session_response': '_on_message_end_session_response',
        'snapshot_response': '_dispatch_session_message',
        'widget_action': '_dispatch_session_message',
        'widget_action_response': '_dispatch_session_message',
        'widget_children_changed': '_dispatch_session_message',
    }

    def __init__(self, router, factories, username='local_qt_client'):
        """ Initialize a QtLocalClient.

        Parameters
        ----------
        router : QRouter
            The QRouter instance to use for sending and receiving
            messages from the local server.

        factories : dict
            A dictionary of factory functions to use for creating the
            client widgets for a view.

        username : str, optional
            The username to use for this client. The default username 
            is 'local_qt_client'

        """
        self._router = router
        self._factories = factories
        self._username = username
        self._initial_sessions = []
        self._session_factories = {}
        self._client_sessions = {}
        self._started = False
        self._router.clientMessagePosted.connect(
            self._on_client_message_posted, Qt.QueuedConnection
        )

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    @log_exceptions
    def _on_client_message_posted(self, message):
        """ A signal handler for the 'clientMessagePosted' signal on the
        router.

        This handler will dispatch the message to the proper message
        handler, or log an error if the message is malformed. Any 
        exceptions raised by this dispatcher will also be logged.

        Parameters
        ----------
        message : Message
            The Message object that was sent from the Enaml server.

        """
        msg_type = message.header.msg_type
        routes = self._message_routes
        if msg_type in routes:
            route = routes[msg_type]
            getattr(self, route)(message)
        else:
            # XXX show a dialog error message?
            msg = 'Received invalid message type from server: %s'
            logging.error(msg % msg_type)

    def _on_message_start_session_response(self, message):
        """ Handle the 'start_session_response' message type.

        This handler will create a new QtSession object to communicate
        with the Enaml server session that was started. If the session
        did not start with status "ok", an error will be logged.

        Parameters
        ----------
        message : Message
            The Message object that was sent from the Enaml server.

        """
        content = message.content
        if content.status == 'ok':
            session_id = content.session
            if session_id in self._client_sessions:
                # XXX show a dialog error message
                msg = "Session id already exists: %s"
                logging.error(msg % session_id)
                return

            parent_msg_id = message.parent_header.msg_id
            client_session_factory = self._session_factories.pop(parent_msg_id,
                None)
            if client_session_factory is None:
                # XXX show a dialog error message
                msg = "No session factory for message id: %s."
                logging.error(msg % parent_msg_id)
                client_session_factory = QtClientSession

            client_session = client_session_factory(
                session_id, self._username, self._router, self._factories,
            )
            self._client_sessions[session_id] = client_session
            client_session.open()
        else:
            # XXX show a dialog error message?
            msg = 'Start session failed with message from server: %s'
            logging.error(msg % content.status_msg)

    def _on_message_end_session_response(self, message):
        """ Handle the 'end_session_response' message type.

        This handler will close the old QtClientSession object. If
        the sever session did not close with status "ok", an error 
        will be logged.

        Parameters
        ----------
        message : Message
            The Message object sent from the Enaml server.

        """
        if message.content.status == 'ok':
            session_id = message.header.session
            if session_id not in self._client_sessions:
                # XXX show a dialog error message
                msg = "Invalid session id: %s"
                logging.error(msg % session_id)
                return
            client_session = self._client_sessions.pop(session_id)
            client_session.close()
        else:
            # XXX show a dialog error message?
            msg = 'End session failed with message from server: %s'
            logging.error(msg % message.content.status_msg)

    def _dispatch_session_message(self, message):
        """ Route a message to a client session.

        This handler is called when the message type is one that should
        be handled by a client session. If the client session doesn't
        exist, then an error message will be logged.

        Parameters
        ----------
        message : Message
            The Message object sent by the server.

        """
        session_id = message.header.session
        if session_id in self._client_sessions:
            self._client_sessions[session_id].handle_message(message)
        else:
            # XXX show a dialog error message?
            msg = 'Invalid session id: %s'
            logging.error(msg % session_id)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _start_session(self, name, client_session_factory):
        msg_id = _qtclient_message_id_gen.next()
        self._session_factories[msg_id] = client_session_factory
        header = {
            'session': None,
            'username': self._username,
            'msg_id': msg_id,
            'msg_type': 'start_session',
            'version': '1.0',
        }
        content = {'name': name}
        message = Message((header, {}, {}, content))
        self._router.appMessagePosted.emit(message)
        
    
    def _start_sessions(self):
        """ A private method which starts the sessions for the client.

        This method is called by the public 'startup' method when the
        client should make requests from the server to start its 
        sessions.

        """
        for name, client_session_factory in self._initial_sessions:
            self._start_session(name, client_session_factory)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def startup(self):
        """ A method which can be called to startup the client sessions.

        This method will be called by the QtLocalApplication on app
        startup. It should not normally be called by user code. 

        """
        self._router.addCallback(self._start_sessions)
        self._started = True
        
    def start_session(self, name, client_session_factory=QtClientSession):
        """ A public method used to request a local session to start
        after the local server is started.

        Parameters
        ----------
        name : str
            The name of the session to start when the server is 
            spooled up.

        """
        if not self._started:
            self._initial_sessions.append((name, client_session_factory))
        # XXX handle dynamic session additions

