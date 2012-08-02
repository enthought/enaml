#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging


class Application(object):
    """ The app server which manages the top-level communication
    protocol for serving Enaml applications.

    """
    #: A message dispatch table used to speed up message routing
    _message_routes = {
        'discover': '_on_message_discover',
        'start_session': '_on_message_start_session',
        'end_session': '_on_message_end_session',
        'snapshot': '_dispatch_session_message',
        'widget_action': '_dispatch_session_message',
        'widget_action_response': '_dispatch_session_message',
    }

    def __init__(self, handlers):
        """ Initialize an Enaml Application.

        Parameters
        ----------
        handlers : iterable of session handlers

        """
        self._all_handlers = []
        self._named_handlers = {}
        self._sessions = {}
        self.add_handlers(handlers)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def _on_message_discover(self, request):
        """ Handle the 'discover' message type.

        This handler will create the list of session info objects and
        send the reponse to the client.

        Parameters
        ----------
        request : BaseRequest
            The request object containing the message sent by client.

        """
        sessions = [{'name': h.session_name, 'description': h.session_description} 
            for h in self._all_handlers
        ]
        content = {'sessions': sessions}
        request.send_ok_response(content=content)

    def _on_message_start_session(self, request):
        """ Handle the 'start_session' message type.

        This handler will create a new session object for the requested
        session type and respond to the client with the new session id.
        If the session type is invalid, the handler will reply with an
        appropriate error message.

        Parameters
        ----------
        request : BaseRequest
            The request object containing the message sent by client.

        """
        message = request.message
        name = message.content.name
        if name not in self._named_handlers:
            request.send_error_response('Invalid session name')
        else:
            # XXX Do we want to move this to a call later, and do some
            # checking on the number of open sessions etc?
            handler = self._named_handlers[name]
            session = handler(request)
            session_id = session.session_id
            self._sessions[session_id] = session
            session.open()
            content = {'session': session_id}
            request.send_ok_response(content=content)

    def _on_message_end_session(self, request):
        """ Handle the 'end_session' message type.

        This handler will close down the existing session and send a
        reponse to the client. If the session id is not valid, an
        appropriate error message will be sent back to the client.

        Parameters
        ----------
        request : BaseRequest
            The request object containing the message sent by client.

        """
        session_id = request.message.header.session
        if session_id not in self._sessions:
            request.send_error_response('Invalid session id')
        else:
            session = self._sessions.pop(session_id)
            session.close()
            request.send_ok_response()

    def _dispatch_session_message(self, request):
        """ Handle a message type that should be routed to a session.

        This handler will lookup the session for the given session id
        and route the message to that object. If the id is invalid, 
        then an appropriate error message will be sent to the client.

        Parameters
        ----------
        request : BaseRequest
            The request object containing the message sent by client.

        """
        session_id = request.message.header.session
        if session_id not in self._sessions:
            request.send_error_response('Invalid session id')
        else:
            session = self._sessions[session_id]
            session.handle_request(request)

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
            name = handler.session_name
            if name in named_handlers:
                msg = 'Multiple session handlers named `%s`; ' % name
                msg += 'replacing previous value.'
                logging.warn(msg)
                old_handler = named_handlers.pop(name)
                all_handlers.remove(old_handler)
            all_handlers.append(handler)
            named_handlers[name] = handler

    def handle_request(self, request):
        """ Route and process a message for the Enaml application.

        This method should be called by the running event loop when it
        receives a message from a client. The event loop should guard 
        this call in a try-except block. Any exceptions raised should 
        be considered as failures in the structure of the message and
        handled appropriately.

        Parameters
        ----------
        request : BaseRequest

        """
        msg_type = request.message.header.msg_type
        route = self._message_routes.get(msg_type)
        if route is not None:
            getattr(self, route)(request)
        else:
            self._send_error_response(request, 'Invalid message type')

