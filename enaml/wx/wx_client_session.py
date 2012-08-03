#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from enaml.utils import id_generator
from enaml.message import Message


#: The global message id generator for this wx process.
_wxsession_message_id_gen = id_generator('wxsmsg_')


class WxClientSession(object):
    """ An object representing the connection between an Enaml server 
    Session and the Wx representation of that session.

    """
    #: A message routing table to speed up dispatching.
    _message_routes = {
        'snapshot_response': '_on_message_snapshot_response',
        'widget_action': '_dispatch_widget_message',
        'widget_action_response': '_dispatch_widget_message',
    }

    def __init__(self, session_id, username, router, factories):
        """ Initialize a WxClientSession.

        Parameters
        ----------
        session_id : str
            The session identifier to use for communicating with the 
            Enaml session object.

        username : str
            The username to associate with the session.

        router : wxRouter
            The wxRouter instance to use for sending messages back to 
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
            self._create_widgets(content.snapshot)
        else:
            msg = 'Snapshot error from server: %s'
            logging.error(msg % content.status_msg)

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
    def _create_widgets(self, trees):
        """ A private method which constructs the widgets for this 
        session.

        Parameters
        ----------
        trees : list of dicts
            A list of dictionaries representing the UI trees to 
            construct for the session.

        """
        widgets = self._widgets
        factories = self._factories

        # XXX destroy the old widgets
        widgets.clear()

        # The flat list of widgets created for the session
        created = []

        # This loop recursively builds out the trees, starting with 
        # parents and moving to children. Toplevel tree components 
        # are expected to take None as a parent.
        for tree in trees:
            stack = [tree]
            parents = [None]
            while stack:
                tree_item = stack.pop()
                parent = parents.pop()
                widget_id = tree_item['widget_id']

                # Walk along the types mro to see if we have a factory
                # that can handle the widget type. The 'class' of the
                # tree item is also the first item in 'bases', so there
                # is no need to test it separately.
                for base in tree_item['bases']:
                    if base in factories:
                        widget_cls = factories[base]()
                        break
                else:
                    # XXX what do we really want to do here? 
                    msg =  'Unhandled widget type: %s:%s'
                    item_class = tree_item['class']
                    item_bases = tree_item['bases']
                    logging.error(msg % (item_class, item_bases))
                    continue # This skips any children as well

                widget = widget_cls(parent, widget_id, self)
                widgets[widget_id] = widget
                created.append((widget, tree_item))

                # Push the children in reverse order so they get 
                # popped off in the correct order.
                for ctree in reversed(tree_item['children']):
                    stack.append(ctree)
                    parents.append(widget)

        # Create and initialize the widgets top-down
        for widget, tree in created:
            widget.create(tree)

        # Run the post creation pass top-down
        for widget, tree in created:
            widget.post_create()

        # Run the layout initializtion bottom-up
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
            'msg_id': _wxsession_message_id_gen.next(),
            'msg_type': 'snapshot',
            'version': '1.0',
        }
        message = Message((header, {}, {}, {}))
        self._router.PostAppMessage(message)

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
            'msg_id': _wxsession_message_id_gen.next(),
            'msg_type': 'widget_action',
            'version': '1.0',
        }
        metadata = {'widget_id': widget_id, 'action': action}
        message = Message((header, {}, metadata, content))
        self._router.PostAppMessage(message)

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

