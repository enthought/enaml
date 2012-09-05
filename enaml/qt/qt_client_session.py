#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from enaml.utils import id_generator
from enaml.message import Message


#: The global message id generator for this qt process.
_qtsession_message_id_gen = id_generator('qtsmsg_')


class QtClientSession(object):
    """ An object representing the connection between an Enaml server 
    Session and the Qt representation of that session.

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
        self._proxies = {}

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
            'msg_id': _qtsession_message_id_gen.next(),
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
            'msg_id': _qtsession_message_id_gen.next(),
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

    def get_proxy_widget(self, proxy, parent):
        """ A method to get or create an appropriate Qt proxy widget.

        This method is called directly by a QtProxyWidget when
        it creates itself. By default, this method looks up the proxy_id
        and calls the object it gets.

        Parameters
        ----------
        proxy : QtProxyWidget
            The QtProxyWidget instance.

        parent : QWidget or None
            The parent QWidget for the proxy.

        """
        print proxy, proxy._proxy_id, self._proxies
        proxy_factory = self._proxies[proxy._proxy_id]
        return proxy_factory(self, proxy, parent)
