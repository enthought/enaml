#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from traits.api import Instance, Str, WeakRef, Property, Bool

from enaml.core.declarative import Declarative
from enaml.session import Session
from enaml.utils import LoopbackGuard, id_generator


#: The global widget identifier generator
_widget_id_gen = id_generator('w_')


class MessengerWidget(Declarative):
    """ The base class of all widget classes in Enaml.

    This extends Declarative with the ability to send and receive
    commands to and from a client.

    """
    #: The session object to use for sending messages to the client.
    #: This will be initially set by the Session object when it takes
    #: ownership of the view. It should not typically be changed by 
    #: user code. Only a weakref to the Session object is stored.
    session = Property(Instance(Session))
    
    #: The unique messaging identifier for this widget. It is generated
    #: automatically and should not typically be changed by user code.
    widget_id = Str
    def _widget_id_default(self):
        return _widget_id_gen.next()

    #: A loopback guard which can be used to prevent a loopback cycle
    #: of messages when setting attributes from within a handler.
    loopback_guard = Instance(LoopbackGuard, ())

    #: The internal storage for the 'session' property. This will be
    #: updated by calls to the 'set_session' method.
    _session = WeakRef(Session)

    #: An internal flag indicating whether or not the change handlers
    #: for the widget have been bound.
    _bound = Bool(False)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _get_session(self):
        """ The property getter for the 'session' property.

        """
        return self._session

    def _children_changed_handler(self, event):
        """ A trait change handler for the `children_changed` event.

        This handler will assemble a child event for the client 
        application and hand it off to the Session object.

        """
        session = self.session
        if session is None:
            msg = 'No Session object for widget %s:%s'
            logging.warn(msg % (self.class_name, self.widget_id))
        else:
            removed = [item.widget_id for item in event['removed']]
            added = [(idx, item.snapshot()) for idx, item in event['added']]
            content = {'added': added, 'removed': removed}
            session.send_children_changed(self.widget_id, content)

    def _publish_attr_handler(self, name, new):
        """ A trait change handler which will send an attribute change
        message to the client.

        The message action will be created by prefixing the attribute
        name with 'set_'. The value of the attribute is expected to be 
        serializable to JSON. The content of the message will have the
        name of the attribute as a key, and the value as its value. If
        the loopback guard is held for the given name, then the message
        will no be sent (avoiding potential loopbacks).

        """
        if name not in self.loopback_guard:
            action = 'set_' + name
            content = {name: new}
            self.send_action(action, content)

    def _bind(self):
        """ A private method for triggering the bind() call.

        This method will only call the public bind() the first time
        this method is called. All other calls will be ignored.

        """
        if not self._bound:
            self.bind()
            self._bound = True

    #--------------------------------------------------------------------------
    # Messaging/Session API
    #--------------------------------------------------------------------------
    def set_session(self, session):
        """ Apply the session object to this component and its subtree.

        This method will be called by the Session object when it takes
        ownership of the view. If may be called later by child change
        handlers to make sure the whole tree is operating on the same
        session. This method should not typically be called by user
        code.

        Parameters
        ----------
        session : Session
            The Session object which should be used by this view.

        """
        self._session = session
        session.register_widget(self)
        self._bind()
        for child in self.children:
            if isinstance(child, MessengerWidget):
                child.set_session(session)

    def handle_action(self, action, content):
        """ Handle an action sent from the client of this widget.

        This is called by the widget's Session object when the client
        of the widget sends a message to this widget.

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
            # XXX probably want to raise an exception so the Session
            # can convert it into an error response.
            msg = "Unhandled action '%s' sent to widget %s:%s"
            logging.warn(msg % (action, self.class_name, self.widget_id))

    def send_action(self, action, content):
        """ Send an action to the client of this widget.

        This method can be called to send an unsolicited message of
        type 'widget_action' to the client of this widget.

        Parameters
        ----------
        action : str
            The action for the message.

        content : dict
            The content of the message.

        """
        session = self.session
        if session is None:
            msg = 'No Session object for widget %s:%s'
            logging.warn(msg % (self.class_name, self.widget_id))
        else:
            session.send_action(self.widget_id, action, content)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ An overridden method which updates the superclass snapshot.

        """
        snap = super(MessengerWidget, self).snapshot()
        snap['widget_id'] = self.widget_id
        return snap

    def bind(self):
        """ A method which should be called when preparing a widget for
        publishing.

        The intent of this method is to allow a widget to hook up its
        trait change notification handlers which will send messages to
        the client. It's assumed that this method will only be called
        once by the object which manages the process of preparing a 
        widget for communication.

        """
        handler = self._children_changed_handler
        self.on_trait_change(handler, 'children_changed')

    def publish_attributes(self, *attrs):
        """ A convenience method provided for subclasses to use to 
        publish an arbitrary number of attributes to the client widet.

        The action for the message is created by prefixing 'set-' to the
        name of the changed attribute. This method is not intended to 
        meet the needs of *all* attribute publishing. Rather it is meant
        to handle most of the simple cases. More complex cases will need
        to implement their own dispatching handlers.

        Parameters
        ----------
        attrs
            The string names of the attributes to publish to the client.
            The values of these attributes are expected to be JSON
            serializable. More complex values should use their own 
            dispatch handlers.

        """
        otc = self.on_trait_change
        handler = self._publish_attr_handler
        for attr in attrs:
            otc(handler, attr)

    def set_guarded(self, **attrs):
        """ A convenience method provided for subclasses to set a
        sequence of attributes from within a loopback guard.

        Parameters
        ----------
        attrs
            The attributes which should be set on the component from
            within a loopback guard context.

        """
        with self.loopback_guard(*attrs):
            for name, value in attrs.iteritems():
                setattr(self, name, value)

