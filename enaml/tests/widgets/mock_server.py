import logging

from enaml.core.signaling import Signal
from enaml.message import Message
from enaml.request import BaseRequest, BasePushHandler
from enaml.utils import id_generator

logger = logging.getLogger(__name__)

def mock_factory():
    from .mock_widget import MockWidget
    return MockWidget


MOCK_FACTORIES = {
    'Action': mock_factory,
    'ActionGroup': mock_factory,
    'Calendar': mock_factory,
    'CheckBox': mock_factory,
    'ComboBox': mock_factory,
    'Container': mock_factory,
    'DateSelector': mock_factory,
    'DatetimeSelector': mock_factory,
    'DockPane': mock_factory,
    'Field': mock_factory,
    'Form': mock_factory,
    'GroupBox': mock_factory,
    'Html': mock_factory,
    'ImageView': mock_factory,
    'Label': mock_factory,
    'MainWindow': mock_factory,
    'MdiArea': mock_factory,
    'MdiWindow': mock_factory,
    'Menu': mock_factory,
    'MenuBar': mock_factory,
    'Notebook': mock_factory,
    'Page': mock_factory,
    'PushButton': mock_factory,
    'ProgressBar': mock_factory,
    'RadioButton': mock_factory,
    'ScrollArea': mock_factory,
    'Slider': mock_factory,
    'SpinBox': mock_factory,
    'Splitter': mock_factory,
    'Stack': mock_factory,
    'StackItem': mock_factory,
    'TextEditor': mock_factory,
    'ToolBar': mock_factory,
    'Window': mock_factory,
    'WidgetComponent': mock_factory,
}



class MockRouter(object):
    """ A simple traits subclass which assists in routing messages in
    a synchronized fashion.

    """
    appMessagePosted = Signal()
    clientMessagePosted = Signal()
    callbackPosted = Signal()

    def __init__(self):
        """ Initialize a QRouter.

        """
        self.callbackPosted.connect(self._onCallbackPosted)

        self.callbackPosted.connect(self.debug_message)
        self.clientMessagePosted.connect(self.debug_message)
        self.appMessagePosted.connect(self.debug_message)


    def debug_message(self, message):
        logger.debug(message)


    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def _onCallbackPosted(self, message):
        """ The signal handler for the 'callbackPosted' signal.

        This handler is invoked via a Qt.QueuedConnection and hence
        will execute aynchronously. Exceptions raised in the callback
        will generate an error log.

        Parameters
        ----------
        item : 3-tuple
            The tuple of callback, args, kwargs emitted on the signal.

        """
        callback, args, kwargs = message
        callback(*args, **kwargs)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def addCallback(self, callback, *args, **kwargs):
        """ Add the callback to the queue to be run in the future.

        Parameters
        ----------
        callback : callable
            The callable to be run at some point in the future.

        *args, **kwargs
            The positional and keyword arguments to pass to the 
            callable when it is invoked.

        """
        item = (callback, args, kwargs)
        self.callbackPosted.emit(item)


class MockPushHandler(BasePushHandler):
    """ A Mock BasePushHandler implementation for the test suite.

    """

    def __init__(self, router):
        """ Initialize a QtLocalPushHandler.

        Parameters
        ----------
        router : QRouter
            The QRouter instance with which to issue requests and 
            callbacks.

        """
        self._router = router

    def push_message(self, message):
        """ Push the given message to the client.

        Parameters
        ----------
        message : Message
            The Message instance that should be pushed to the client.

        """
        self._router.clientMessagePosted.emit(message)

    def add_callback(self, callback, *args, **kwargs):
        """ Add a callback to the event queue to be called later.

        This is used as a convenience for Session objects to provide
        a way to run callables in a deferred fashion. It does not 
        imply any communication with the client. It is merely an
        abstract entry point into the zmq event loop. 

        Call it a concession to practicality over purity - SCC

        Parameters
        ----------
        callback : callable
            A callable which should be invoked by the event loop at 
            some future time. This method returns immediately.

        *args, **kwargs
            The positional and keyword arguments to pass to the 
            callable when it is invoked.

        """
        self._router.addCallback(callback, *args, **kwargs)



class MockRequest(BaseRequest):
    """ A mock BaseRequest implementation for the test suite.

    """

    def __init__(self, message, router):
        """ Initialize a MockRequest.

        Parameters
        ----------
        message : Message
            The Message instance that generated this request.

        router : MockRouter
            The MockRouter instance with which to issue replies and
            callbacks.

        """
        self._message = message
        self._router = router
        self._finished = False


    @property
    def message(self):
        return self._message


    def add_callback(self, callback, *args, **kwargs):
        """ Add a callback to the event queue to be called later.

        This is can be used by the request handlers to defer long 
        running work until a future time, at which point the results
        can be pushed to the client with the 'push_handler()'.

        Parameters
        ----------
        callback : callable
            A callable which should be invoked by the event loop at 
            some future time. This method will return immediately.

        *args, **kwargs
            The positional and keyword arguments to pass to the 
            callable when it is invoked.

        """
        self._router.addCallback(callback, *args, **kwargs)

    def send_response(self, message):
        """ Send the given message to the client as a reply.

        Parameters
        ----------
        message : Message
            A Message instance to send to the client as a reply to
            this particular request.

        """
        if self._finished:
            raise RuntimeError('Request already finished')
        self._router.clientMessagePosted.emit(message)
        self._finished = True

    def push_handler(self):
        """ Returns an object that can be used to push unsolicited 
        messages to this client.

        Returns
        -------
        result : QtLocalPushHandler
            A QtLocalPushHandler instance which can be used to push 
            messages to this client, without the client initiating a 
            request.

        """
        return MockPushHandler(self._router)

SESSION_ID_GEN = id_generator('__mockmsg_session')

class MockClientSession(object):
    """ An object representing the connection between an Enaml server
    Session and the representation of that session.

    """
    #: A message routing table to speed up dispatching.
    _message_routes = {
        'snapshot_response': '_on_message_snapshot_response',
        'widget_action': '_dispatch_widget_message',
        'widget_action_response': '_dispatch_widget_message',
        'widget_children_changed': '_on_message_widget_children_changed',
    }

    def __init__(self, session_id, username, router, factories):
        """ Initialize a QtClientSession.

        Parameters
        ----------
        session_id : str
            The session identifier to use for communicating with the 
            Enaml session object.

        username : str
            The username to associate with the session.

        router : QRouter
            The QRouter instance to use for sending messages back to 
            the client.

        factories : dict
            The Qt factory functions to use when building the view.

        """
        self._session_id = session_id
        self._username = username
        self._router = router
        self._factories = factories
        self._widgets = {}

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def _on_message_snapshot_response(self, message):
        """ Handle the 'snapshot_response' message type.

        This method will clear all of the existing widgets for the 
        session, and rebuild the UI tree(s) to match the state on the
        server. If the status of the response is not "ok", then an
        error will be logged.

        Parameters
        ----------
        message : Message
            The Message object sent from the server.

        """
        content = message.content
        if content.status == 'ok':
            # XXX destroy the old widgets
            self._widgets.clear()
            child_defs = [(-1, item) for item in content.snapshot]
            self._build_children(None, child_defs)
        else:
            msg = 'Snapshot error from server: %s'
            logging.error(msg % content.status_msg)

    def _on_message_widget_children_changed(self, message):
        """ Handle the 'widget_children_changed' message type.

        This method will destroy the children removed from the widget
        and create and add the new children to the tree.

        Parameters
        ----------
        message : Message
            The Message object sent from the server.

        """
        content = message.content
        for widget_id in content.removed:
            widget = self._widgets.get(widget_id)
            if widget is not None:
                widget.destroy()
        parent = self._widgets.get(message.metadata.widget_id)
        self._build_children(parent, content.added)

    def _dispatch_widget_message(self, message):
        """ Route a 'widget_action' message to the client widget.

        This handler will lookup the widget using the given widget
        id and pass the action and message content to the action
        handler on the widget. If the widget does not exist, then
        an error will be logged.

        TODO - handle the "widget_action_response" message type.
        
        Parameters
        ----------
        message : Message
            The Message object sent from the server.

        """
        if message.header.msg_type == 'widget_action':
            widget_id = message.metadata.widget_id
            if widget_id not in self._widgets:
                msg = 'Invalid widget id from server: %s'
                logging.error(msg % widget_id)
                return
            widget = self._widgets[widget_id]
            widget.handle_action(message.metadata.action, message.content)
        # XXX handle msg_type 'widget_action_response'

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _build_widget(self, parent, tree_item, factories):
        """ A private method which constructs the given widget.

        Parameters
        ----------
        parent : QtMessengerWidget or None
            The widget to use a parent for the widget being built.

        tree_item : dict
            The dictionary representing the UI tree for the widget.
            Only the root level widget will be built.

        factories : dict
            The dict of factories to use for building the widget.

        Returns
        -------
        result : QtMessengerWidget or None
            The built widget, or None if the widget could not be built.
            A failed build will be logged as an error. The returned
            widget is *not* added to the parent. That responsibility
            lies with the caller.

        """
        # Walk along the types mro to see if we have a factory
        # that can handle the widget type. The 'class' of the
        # tree item is also the first item in 'bases', so there
        # is no need to test it separately.
        for base in tree_item['bases']:
            if base in factories:
                widget_cls = factories[base]()
                return widget_cls(parent, tree_item['widget_id'], self)
        else:
            # XXX what do we really want to do here? 
            msg =  'Unhandled widget type: %s:%s'
            item_class = tree_item['class']
            item_bases = tree_item['bases']
            logging.error(msg % (item_class, item_bases))

    def _build_children(self, parent, child_defs):
        """ A private method which builds the children of a parent.

        Parameters
        ----------
        parent : QtMessengerWidget or None
            The messenger widget to use as the parent of the widgets
            being created, or None if they have no parent.

        child_defs : list of tuples
            A list of the form (index, snapshot) where index is the
            integer index to use when inserting the newly built child
            into the parent. If the index is -1, the child will be 
            simply added to the parent. The 'snapshot' is the dict
            representing the ui tree to build for the child. 

        """
        # The dict of widget_id -> widget used for message dispatching
        widgets = self._widgets

        # The dict of factories to use for finding the right widget
        # class to use when building a widget.
        factories = self._factories

        # The flat list of widgets created during this build pass. The
        # widgets are collected so that the initialization passes can
        # be performed without traversing the tree. 
        created = []

        # Pre-fetch the bound method for actually building a widget.
        build = self._build_widget

        # A stack used for pushing tree items and their index
        tree_stack = []
        tree_push = tree_stack.append
        tree_pop = tree_stack.pop

        # A stack used pushing parent items
        parent_stack = []
        parent_push = parent_stack.append
        parent_pop = parent_stack.pop

        # This loop recursively builds out the trees, starting with 
        # parents and moving to children. Toplevel tree components 
        # are expected to take None as a parent.
        for index, tree in child_defs:
            tree_push((index, tree))
            parent_push(parent)
            while tree_stack:
                tree_index, tree_item = tree_pop() 
                parent = parent_pop()
                widget = build(parent, tree_item, factories)
                if widget is None:
                    # widget build failed; logged to error
                    continue
                if parent is not None:
                    if tree_index == -1:
                        parent.add_child(widget)
                    else:
                        parent.insert_child(tree_index, widget)
                widgets[widget.widget_id()] = widget
                created.append((widget, tree_item))
                for child_tree in reversed(tree_item['children']):
                    tree_push((-1, child_tree))
                    parent_push(widget)

        # Create and initialize the widgets top-down
        for widget, tree in created:
            widget.create(tree)

        # Run the layout initialization bottom-up
        for widget, tree in reversed(created):
            widget.init_layout()
    
    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self):
        """ Open the session view.

        This method will initiate a snapshot fetch from the server.
        When the response is returned, the session will be the ui for
        the snapshot and display it on the screen.

        """
        header = {
            'session': self._session_id,
            'username': self._username,
            'msg_id': SESSION_ID_GEN.next(),
            'msg_type': 'snapshot',
            'version': '1.0',
        }
        message = Message((header, {}, {}, {}))
        self._router.appMessagePosted.emit(message)

    def send_action(self, widget_id, action, content):
        """ Send an unsolicited message of type 'widget_action' to a
        server widget for this session.

        This method is normally only called by the QtMessengerWidget's
        which are owned by this QtClientSession object. This should not 
        be called directly by user code.
        
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
            'msg_id': SESSION_ID_GEN.next(),
            'msg_type': 'widget_action',
            'version': '1.0',
        }
        metadata = {'widget_id': widget_id, 'action': action}
        message = Message((header, {}, metadata, content))
        self._router.appMessagePosted.emit(message)

    def handle_message(self, message):
        """ A method called by the application when the server sends a
        message to the client.

        Parameters
        ----------
        message : Message
            The Message object to be handled

        """
        # The application has already verified that the msg_type is a 
        # supported message type of the session. So it this results in
        # a KeyError, then it's a problem with the implementation.
        msg_type = message.header.msg_type
        route = self._message_routes[msg_type]
        getattr(self, route)(message)

    def widget_destroyed(self, widget_id):
        """ A method called when a messenger widget is destroyed.

        This method is called directly by a QtMessengerWidget when
        it destroys itself. This allows the session to remove its
        reference to the widget. This should not be called by user
        code.

        Parameters
        ----------
        widget_id : str
            The identifier of the widget which has been destroyed.

        """
        self._widgets.pop(widget_id, None)



ID_GEN = id_generator('__mockmsg')

class MockLocalClient(object):
    """ A client for managing server sessions in an in-process 
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

    def __init__(self, router, factories, username='mock_local_client'):
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
        self._session_names = []
        self._client_sessions = {}
        self._started = False
        self._router.clientMessagePosted.connect(self._on_client_message_posted)


    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
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
            client_session = MockClientSession(
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
    def _start_sessions(self):
        """ A private method which starts the sessions for the client.

        This method is called by the public 'startup' method when the
        client should make requests from the server to start its 
        sessions.

        """
        for name in self._session_names:
            header = {
                'session': None,
                'username': self._username,
                'msg_id': ID_GEN.next(),
                'msg_type': 'start_session',
                'version': '1.0',
            }
            content = {'name': name}
            message = Message((header, {}, {}, content))
            self._router.appMessagePosted.emit(message)

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

    def start_session(self, name):
        """ A public method used to request a local session to start
        after the local server is started.

        Parameters
        ----------
        name : str
            The name of the session to start when the server is 
            spooled up.

        """
        if not self._started:
            self._session_names.append(name)
        # XXX handle dynamic session additions


class MockLocalServer(object):
    """ An Enaml Application server which executes in the local process
    and a set of mock classes.

    Since this is a locally running in-process server, the Enaml 
    messages skip the serialization to JSON step.

    """
    def __init__(self, app, factories=None):
        """ Initialize at MockLocalServer.

        Parameters
        ----------
        app : Application
            The Enaml application object that should be served.

        factories : dict, optional
            A dictionary of client widget factories to use for the
            application. If not provided, the defaults will be used.

        """

        # The enaml application that is being served by this server.
        self._app = app

        # The QRouter to use for message passing.
        self._router = MockRouter()
        self._router.appMessagePosted.connect(self._on_app_message_posted)


        # The local client that will manage the client sessions
        self._client = MockLocalClient(self._router, factories or MOCK_FACTORIES)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def _on_app_message_posted(self, message):
        """ A handler for the 'appMessagePosted' signal on the QRouter.

        This method will be invoked when the client needs to send a
        message to the Enaml application.

        Parameters
        ----------
        message : Message
            The message object to pass to the Enaml Application.

        """
        request = MockRequest(message, self._router)
        self._app.handle_request(request)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def local_client(self):
        """ Return a handle to the local client instance for the server.

        Since this is a locally running server, there is a singleton
        instance of QtLocalClient that is used to manage the qt view
        sessions.

        Returns
        -------
        result : QtLocalClient
            The singleton local client instance used for managing the
            local qt session objects. The 'start_session' method on
            this object should be used to start a new view session.

        """
        return self._client

    def start(self):
        """ Start the sever's main loop.

        This will enter the main GUI event loop and block until a call
        to 'stop' is made, at which point this method will return.

        """
        self._client.startup()

    def stop(self):
        """ Stop the server's main loop.

        Calling this method will cause a previous call to 'start' to 
        unblock and return.

        """
        pass

