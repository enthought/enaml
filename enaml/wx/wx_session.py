#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from enaml.dispatch import dispatch_action

from .wx_object import WxObject
from .wx_widget_registry import WxWidgetRegistry


logger = logging.getLogger(__name__)


class WxSession(object):
    """ An object which manages a session of Wx client objects.

    """
    def __init__(self, session_id, widget_groups):
        """ Initialize a WxSession.

        Parameters
        ----------
        session_id : str
            The string identifier for this session.

        widget_groups : list of str
            The list of string widget groups for this session.

        """
        self._session_id = session_id
        self._widget_groups = widget_groups
        self._socket = None
        self._objects = []

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self, snapshot, socket):
        """ Open the session using the given snapshot and socket.

        Parameters
        ----------
        snaphshot : list of dicts
            The list of tree snapshots to build for this session.

        socket : ActionSocketInterface
            The socket interface to use for messaging.

        """
        objects = self._objects
        for tree in snapshot:
            obj = self.build(tree, None)
            if obj is not None:
                obj.initialize()
                objects.append(obj)
        # Setup the socket after initialization so that any messages
        # generated during initialization are ignored.
        self._socket = socket
        socket.on_message(self.on_message)

    def close(self):
        """ Close the session and release all object references.

        """
        for obj in self._objects:
            obj.destroy()
        self._objects = []
        socket = self._socket
        if socket is not None:
            socket.on_message(None)

    def build(self, tree, parent):
        """ Build and return a new widget using the given tree dict.

        Parameters
        ----------
        tree : dict
            The dictionary snapshot representation of the tree of
            items to build.

        parent : WxObject or None
            The parent for the tree, or None if the tree is top-level.

        Returns
        -------
        result : WxObject or None
            The object representation of the root of the tree, or None
            if it could not be built. If the object cannot be built,
            the building errors will be sent to the error logger.

        """
        groups = self._widget_groups
        factory = WxWidgetRegistry.lookup(tree['class'], groups)
        if factory is None:
            for class_name in tree['bases']:
                factory = WxWidgetRegistry.lookup(class_name, groups)
                if factory is not None:
                    break
        if factory is None:
            msg =  'Unhandled object type: %s:%s'
            item_class = tree['class']
            item_bases = tree['bases']
            logger.error(msg % (item_class, item_bases))
            return
        obj = factory().construct(tree, parent, self)
        for child in tree['children']:
            self.build(child, obj)
        return obj

    def send(self, object_id, action, content):
        """ Send a message to a server object.

        This method is called by the `WxObject` instances owned by this
        session to send messages to their server implementations.

        Parameters
        ----------
        object_id : str
            The object id of the server object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        socket = self._socket
        if socket is not None:
            socket.send(object_id, action, content)

    def on_message(self, object_id, action, content):
        """ Receive a message sent to an object owned by this session.

        This is a handler method registered as the callback for the
        action socket. The message will be routed to the appropriate
        `WxObject` instance.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        if object_id == self._session_id:
            obj = self
        else:
            obj = WxObject.lookup_object(object_id)
            if obj is None:
                msg = "Invalid object id sent to WxSession: %s:%s"
                logger.warn(msg % (object_id, action))
                return
        dispatch_action(obj, action, content)

    #--------------------------------------------------------------------------
    # Action Handlers
    #--------------------------------------------------------------------------
    def on_action_message_batch(self, content):
        """ Handle the 'message_batch' action sent by the Enaml session.

        """
        for object_id, action, msg_content in content['batch']:
            obj = WxObject.lookup_object(object_id)
            if obj is None:
                msg = "Invalid object id sent to WxSession: %s:%s"
                logger.warn(msg % (object_id, action))
            else:
                dispatch_action(obj, action, msg_content)

