#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging
from weakref import ref

from enaml.utils import LoopbackGuard


class QtMessengerWidget(object):
    """ The base class of the Qt widgets wrappers for a Qt Enaml client.

    """
    def __init__(self, parent, widget_id, session):
        """ Initialize a QtMessengerWidget

        Parameters
        ----------
        parent : QtMessengerWidget or None
            The parent widget of this widget, or None if this widget has
            no parent.

        widget_id : str
            The identifier string for this widget.

        session : QtClientSession
            The client session object to use for communicating with the
            server widget.

        """
        self._parent_ref = ref(parent) if parent is not None else lambda: None
        self.widget = None
        self.children = []
        self.widget_id = widget_id
        self.session = session
        if parent is not None:
            parent.children.append(self)

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
            logging.warn(msg % (self.widget_id, action))

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
        session = self.session
        if session is None:
            msg = 'No Session object for widget %s'
            logging.warn(msg % self.widget_id)
        else:
            session.send_action(self.widget_id, action, content)

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def parent(self):
        """ A read-only property which returns the parent of this widget.

        """
        return self._parent_ref()

    @property
    def parent_widget(self):
        """ A read-only property which returns the parent qt widget 
        for this client widget, or None if it has no parent.

        """
        parent = self.parent
        if parent is None:
            return None
        return parent.widget

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
    def create(self):
        """ A method which must be implemented by subclasses. 

        This method should create the underlying QWidget object and 
        assign it to the 'widget' attribute. Implementations of this
        method should *not* call the superclass version.

        """
        raise NotImplementedError

    def initialize(self, attributes):
        """ A method called to initialize the attributes of the 
        underlying widget.

        The default implementation of this method is a no-op in order
        to be super() friendly. Implementations of this method should
        call the superclass version to make sure that all attributes
        get properly initialized.

        This method will be called after all other widgets for the
        creation pass have been created.

        Parameters
        ----------
        attributes : dict
            The dictionary of attributes that was contained in the
            payload of the operation for the 'create' action which
            created this widget.

        """
        pass

    def post_initialize(self):
        """ A method that allows widgets to do post initialization work.

        This method is called after all widgets in a creation pass have
        had their 'initialize' method called. It is useful for e.g.
        layout initialization, which requires that all child widgets
        have their attributes already initialized.

        The default implementation of this method is a no-op in order
        to be super() friendly. Implementations of this method should
        call the superclass version to make sure that all post
        initialization is properly performed.

        """
        pass

    def destroy(self):
        """ Destroy this widget by removing all references to it from
        it parent and its children and destroy the underlying Qt widget.

        """
        parent = self.parent
        if parent is not None:
            if self in parent.children:
                parent.children.remove(self)
        self.children = []
        widget = self.widget
        if widget is not None:
            widget.destroy()
            self.widget = None

