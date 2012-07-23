#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple
import logging


SessionSpec = namedtuple(
    'SessionSpec', 'name description session_class kwargs'
)


class Application(object):
    """ The app server which manages the top-level communication
    protocol for serving Enaml applications.

    """
    #: The message types handled by the application. This is used
    #: to speed up message routing and dispatching.
    _app_message_types = set([
        'enaml_discover', 'enaml_begin_session', 'enaml_end_session',
    ])

    def __init__(self, handlers):
        """ Initialize an Enaml Application.

        Parameters
        ----------
        handlers : iterable of tuples

        """
        self._all_handlers = []
        self._named_handlers = {}
        self._sessions = {}
        self.add_handlers(handlers)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def _on_enaml_discover(self, request):
        """ Handle the 'enaml_discover' message type.

        """
        sessions = [dict(name=spec.name, description=spec.description) 
                    for spec in self._all_handlers]
        request.reply(sessions=sessions)

    def _on_enaml_begin_session(self, request):
        """ Handle the 'enaml_begin_session' message type.

        """
        message = request.message
        name = message.content.name
        if name not in self._named_handlers:
            msg = 'Invalid session name: %s' % name
            request.reply('error', msg)
        else:
            handler = self._named_handlers[name]
            session_cls = handler.session_class
            session_kwargs = handler.kwargs
            push_handler = request.push_handler()
            username = message.header.username
            session = session_cls(push_handler, username, kwargs=session_kwargs)
            session_id = session.session_id
            self._sessions[session_id] = session
            session.open()
            request.reply(session=session_id)

    def _on_enaml_end_session(self, request):
        """ Handle the 'enaml_end_session' message type.

        """
        session_id = request.message.header.session
        if session_id not in self._sessions:
            msg = 'Invalid session id'
            request.reply('error', msg)
        else:
            session = self._sessions.pop(session_id)
            session.close()
            request.reply()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def add_handlers(self, handlers):
        """ Add session handlers to the application.

        Parameters
        ----------
        handlers : iterable of tuples

        """
        all_handlers = self._all_handlers
        named_handlers = self._named_handlers
        for handler in handlers:
            if len(handler) == 3:
                name, description, session_class = handler
                kwargs = None
            else:
                name, description, session_class, kwargs = handler
            if name in named_handlers:
                msg = 'Multiple session handlers named `%s`; ' % name
                msg += 'replacing previous value.'
                logging.warn(msg)
                handler = named_handlers.pop(name)
                all_handlers.remove(handler)
            spec = SessionSpec(name, description, session_class, kwargs)
            all_handlers.append(spec)
            named_handlers[name] = spec

    def handle_request(self, request):
        """ Route and process a message for the Enaml application.

        This method should be called by the running event loop when
        it receives a message from a client. The event loop should
        guard this call in a try-except block. Any exceptions raised
        should be considered as total failures in the structure of
        the message, and a reply should not be sent to the client.

        Parameters
        ----------
        request : BaseRequest

        """
        header = request.message.header
        msg_type = header.msg_type
        if msg_type in self._app_message_types:
            handler_name = '_on_' + msg_type
            getattr(self, handler_name)(request)
        else:
            session_id = header.session
            if session_id not in self._sessions:
                msg = 'Invalid session id'
                request.reply('error', msg)
            else:
                session = self._sessions[session_id]
                session.handle_request(request)

