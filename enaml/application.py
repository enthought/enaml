#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging


class Application(object):
    """ The application object which manages the top-level communication
    protocol for serving Enaml views.

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

    def __init__(self, factories):
        """ Initialize an Enaml Application.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances that will be used
            to create the sessions for the application.

        """
        self._all_factories = []
        self._named_factories = {}
        self._sessions = {}
        self.add_factories(factories)

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
            {'name': fact.name, 'description': fact.description} 
            for fact in self._all_factories
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
        if name not in self._named_factories:
            request.send_error_response('Invalid session name')
        else:
            # XXX Do we want to move this to a call later, and do some
            # checking on the number of open sessions etc?
            factory = self._named_factories[name]
            session = factory(request)
            session_id = session.session_id
            self._sessions[session_id] = session
            # XXX Do we want to open() immediately, or wait util the 
            # first snapshot request comes in for the session?
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
    def add_factories(self, factories):
        """ Add session factories to the application.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to add to the 
            application.

        """
        all_factories = self._all_factories
        named_factories = self._named_factories
        for factory in factories:
            name = factory.name
            if name in named_factories:
                msg = 'Multiple session factories named `%s`; ' % name
                msg += 'replacing previous value.'
                logging.warn(msg)
                old_factory = named_factories.pop(name)
                all_factories.remove(old_factory)
            all_factories.append(factory)
            named_factories[name] = factory

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
            The request object which wraps a message sent by a client.

        """
        msg_type = request.message.header.msg_type
        route = self._message_routes.get(msg_type)
        if route is not None:
            getattr(self, route)(request)
        else:
            request.send_error_response(request, 'Invalid message type')

