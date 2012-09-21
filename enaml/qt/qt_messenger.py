#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from enaml.utils import LoopbackGuard


class QtMessenger(object):
    """ The base class of the Qt wrappers for a Qt Enaml client.

    """
    def __init__(self, parent, object_id, session):
        """ Initialize a QtMessenger

        Parameters
        ----------
        parent : QtMessengerWidget or None
            The parent widget of this widget, or None if this widget has
            no parent.

        object_id : str
            The identifier string for this object.

        session : QtClientSession
            The client session object to use for communicating with the
            server widget.

        """
        self._object_id = object_id
        self._session = session
        self._parent = parent # XXX included for compatiability with widgets
        self._object = None

    #--------------------------------------------------------------------------
    # Messaging/Session API
    #--------------------------------------------------------------------------
    def handle_action(self, action, content):
        """ Handle an action sent from the server widget

        This is called by the QtClientSession object when the server
        widget sends a message to this widget.

        Parameters
        ----------
        action : str
            The action to be performed by the widget.

        content : ObjectDict
            The content dictionary for the action.

        """
        handler_name = 'on_action_' + action
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(content)
        else:
            # XXX show a dialog here?
            msg = "Unhandled action sent to `%s` from server: %s"
            logging.warn(msg % (self.widget_id(), action))

    def send_action(self, action, content):
        """ Send an action to the server widget.

        This method can be called to send an unsolicited message of
        type 'widget_action' to the server widget for this widget.

        Parameters
        ----------
        action : str
            The action for the message.

        content : dict
            The content of the message.

        """
        session = self._session
        if session is None:
            msg = 'No Session object for widget %s'
            logging.warn(msg % self.widget_id())
        else:
            session.send_action(self.widget_id(), action, content)

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def loopback_guard(self):
        """ Lazily creates and returns a LoopbackGuard for convenient 
        use by subclasses.

        """
        try:
            guard = self._loopback_guard
        except AttributeError:
            guard = self._loopback_guard = LoopbackGuard()
        return guard

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def object(self):
        """ Get the toolkit object for this messenger object.

        Returns
        -------
        result : object
            The toolkit object for this messenger object, or None if
            it does not have a toolkit object.

        """
        return self._object

    def object_id(self):
        """ Get the object id for the messenger object.

        Returns
        -------
        result : str
            The object identifier for this messenger object.

        """
        return self._object_id


    def create(self, snapshot):
        """ A method called by the application when creating the object.
        
        This should create the underlying toolkit object, if any.

        Parameters
        ----------
        snapshot : dict
            The dictionary representation of the snapshot for this object.

        """
        raise NotImplementedError

    def destroy(self):
        """ Destroy this widget.

        Destruction is performed in the following order:
            1. The object removes itself from its parent.
            2. The parent reference is set to None.
            3. The object removes itself from the session.

        """
        parent = self._parent
        if parent is not None:
            parent.remove_child(self)
        self._parent = None

        self._object = None

        session = self._session
        if session is not None:
            session.object_destroyed(self._object_id)
            self._session = None


