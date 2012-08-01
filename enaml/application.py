#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple
import logging


#: A namedtuple used for storing session specification info
SessionSpec = namedtuple(
    'SessionSpec', 'name description factory args kwargs'
)


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
        handlers : iterable of tuples

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
        sessions = [
            {'name': spec.name, 'description': spec.description} 
            for spec in self._all_handlers
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
            factory = handler.factory
            push_handler = request.push_handler()
            username = message.header.username
            session = factory(push_handler, username)
            session_id = session.session_id
            self._sessions[session_id] = session
            session.open(*handler.args, **handler.kwargs)
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
        lens = (3, 4, 5)
        for handler in handlers:
            n = len(handler)
            if n not in lens:
                raise ValueError('Invalid handler description %s' % handler)
            if n == 3:
                name, description, factory = handler
                args = ()
                kwargs = {}
            elif n == 4:
                name, description, factory, args_or_kwargs = handler
                if isinstance(args_or_kwargs, tuple):
                    args = args_or_kwargs
                    kwargs = {}
                else:
                    args = ()
                    kwargs = args_or_kwargs
            else:
                name, description, factory, args, kwargs = handler
            if name in named_handlers:
                msg = 'Multiple session handlers named `%s`; ' % name
                msg += 'replacing previous value.'
                logging.warn(msg)
                handler = named_handlers.pop(name)
                all_handlers.remove(handler)
            spec = SessionSpec(name, description, factory, args, kwargs)
            all_handlers.append(spec)
            named_handlers[name] = spec

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

