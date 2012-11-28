#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from traits.api import HasTraits, Instance, List, Str, ReadOnly

from enaml.core.object import Object
from enaml.support.resource import ResourceManager

from .application import deferred_call
from .dispatch import dispatch_action
from .signaling import Signal
from .socket_interface import ActionSocketInterface


logger = logging.getLogger(__name__)


#: The set of actions which should be batched and sent to the client as
#: a single message. This allows a client to perform intelligent message
#: handling when dealing with messages that may affect the widget tree.
BATCH_ACTIONS = set(['destroy', 'children_changed', 'relayout'])


class DeferredMessageBatch(object):
    """ A class which aggregates batch messages.

    Each time a message is added to this object, its tick count is
    incremented and a tick down event is posted to the event queue.
    When the object receives the tick down event, it decrements its
    tick count, and if it's zero, fires the `triggered` signal.

    This allows a consumer of the batch to continually add messages and
    have the `triggered` signal fired only when the event queue is fully
    drained of relevant messages.

    """
    #: A signal emitted when the tick count of the batch reaches zero
    #: and the owner of the batch should consume the messages.
    triggered = Signal()

    def __init__(self):
        """ Initialize a DeferredMessageBatch.

        """
        self._messages = []
        self._tick = 0

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _tick_down(self):
        """ A private handler method which ticks down the batch.

        The tick down events are called in a deferred fashion to allow
        for the aggregation of batch events. When the tick reaches
        zero, the `triggered` signal will be emitted.

        """
        self._tick -= 1
        if self._tick == 0:
            self.triggered.emit()
        else:
            deferred_call(self._tick_down)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def release(self):
        """ Release the messages that were added to the batch.

        Returns
        -------
        result : list
            The list of messages added to the batch.

        """
        messages = self._messages
        self._messages = []
        return messages

    def add_message(self, message):
        """ Add a message to the batch.

        This will cause the batch to tick up and then start the tick
        down process if necessary.

        Parameters
        ----------
        message : object
            The message object to add to the batch.

        """
        self._messages.append(message)
        if self._tick == 0:
            deferred_call(self._tick_down)
        self._tick += 1


class Session(HasTraits):
    """ An object representing the session between a client and its
    Enaml objects.

    The session object is what ensures that each client has their own
    individual instances of objects, so that the only state that is
    shared between clients is that which is explicitly provided by the
    developer.

    """
    #: The string identifier for this session. This is provided by
    #: the application in the `open` method. The value should not
    #: be manipulated by user code.
    session_id = ReadOnly

    #: The objects being managed by this session. This list should be
    #: populated by user code during the `on_open` method.
    objects = List(Object)

    #: The resource manager to use for this session. User code can add
    #: resources to the default manager during the `on_open` method, or
    #: replace it with a custom resource manager.
    resources = Instance(ResourceManager, ())

    #: The widget implementation groups which should be used by the
    #: widgets in this session. Widget groups are an advanced feature
    #: which allow the developer to selectively expose toolkit specific
    #: implementations Enaml widgets. All standard Enaml widgets are
    #: available in the 'default' group, which means this value will
    #: rarely need to be changed by the user.
    widget_groups = List(Str, ['default'])

    #: The socket used by this session for communication. This is
    #: provided by the Application in the `open` method. The value
    #: should not normally be manipulated by user code.
    socket = Instance(ActionSocketInterface)

    #: The private deferred message batch used for collapsing layout
    #: related messages into a single batch to send to the client
    #: session for more efficient handling.
    _batch = Instance(DeferredMessageBatch)
    def __batch_default(self):
        batch = DeferredMessageBatch()
        batch.triggered.connect(self._on_batch_triggered)
        return batch

    @classmethod
    def factory(cls, name='', description='', *args, **kwargs):
        """ Get a SessionFactory for this Session class.

        """
        from enaml.session_factory import SessionFactory
        if not name:
            name = cls.__name__
        if not description:
            description = cls.__doc__
        return SessionFactory(name, description, cls, *args, **kwargs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_batch_triggered(self):
        """ A signal handler for the `triggered` signal on the deferred
        message batch.

        """
        content = {'batch': self._batch.release()}
        self.send(self.session_id, 'message_batch', content)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def on_open(self):
        """ Called by the application when the session is opened.

        This method must be implemented in a subclass and is called to
        create the Enaml objects for the session. This method will only
        be called once during the session lifetime.

        Returns
        -------
        result : iterable
            An iterable of Enaml objects for this session.

        """
        raise NotImplementedError

    def on_close(self):
        """ Called by the application when the session is closed.

        This method may be optionally implemented by subclasses so that
        they can perform custom cleaup. After this method returns, the
        session should be considered invalid. This method is only called
        once during the session lifetime.

        """
        pass

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self, session_id, socket):
        """ Called by the application when the session is opened.

        This method will call the `on_open` abstract method which must
        be implemented by subclasses. The method should never be called
        by user code.

        Parameters
        ----------
        session_id : str
            The identifier to use for this session.

        socket : ActionSocketInterface
            A concrete implementation of ActionSocketInterface to use
            for messaging by this session.

        """
        self.session_id = session_id
        self.on_open()
        for obj in self.objects:
            obj.session = self
            obj.initialize()
        self.socket = socket
        socket.on_message(self.on_message)

    def close(self):
        """ Called by the application when the session is closed.

        This method will call the `on_close` method which may be
        implemented by subclasses. The method should never be called
        by user code.

        """
        self.on_close()
        for obj in self.objects:
            obj.destroy()
        self.objects = []
        socket = self.socket
        if socket is not None:
            socket.on_message(None)

    def snapshot(self):
        """ Get a snapshot of this session.

        Returns
        -------
        result : list
            A list of snapshot dictionaries representing the current
            state of this session.

        """
        return [obj.snapshot() for obj in self.objects]

    #--------------------------------------------------------------------------
    # Messaging API
    #--------------------------------------------------------------------------
    def send(self, object_id, action, content):
        """ Send a message to a client object.

        This method is called by the `Object` instances owned by this
        session to send messages to their client implementations.

        Parameters
        ----------
        object_id : str
            The object id of the client object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        socket = self.socket
        if socket is not None:
            if action in BATCH_ACTIONS:
                self._batch.add_message((object_id, action, content))
            else:
                socket.send(object_id, action, content)

    def on_message(self, object_id, action, content):
        """ Receive a message sent to an object owned by this session.

        This is a handler method registered as the callback for the
        action socket. The message will be routed to the appropriate
        `Object` instance.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        if object_id == self.session_id:
            obj = self
        else:
            obj = Object.lookup_object(object_id)
            if obj is None:
                msg = "Invalid object id sent to Session: %s:%s"
                logger.warn(msg % (object_id, action))
                return
        dispatch_action(obj, action, content)

