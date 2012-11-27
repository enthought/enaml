#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import types

from enaml.socket_interface import ActionSocketInterface
from enaml.weakmethod import WeakMethod

from .qt.QtCore import QObject, Signal, QEvent, QCoreApplication


#------------------------------------------------------------------------------
# QActionSocket
#------------------------------------------------------------------------------
class QActionSocket(QObject):
    """ A base class used for implementing action sockets.

    This is a QObject subclass which converts a `send` on the socket
    into a `messagePosted` signal which can be connected to another
    part of the application. Incoming socket messages can be delivered
    to the `receive` method of the socket.

    """
    #: A signal emitted when a message has been sent on the socket.
    messagePosted = Signal(object, object, object)

    def __init__(self):
        """ Initialize a QActionSocket.

        """
        super(QActionSocket, self).__init__()
        self._callback = None

    def on_message(self, callback):
        """ Register a callback for receiving messages sent by a
        client object.

        Parameters
        ----------
        callback : callable
            A callable with an argument signature that is equivalent to
            the `send` method. If the callback is a bound method, then
            the lifetime of the callback will be bound to lifetime of
            the method owner object.

        """
        if isinstance(callback, types.MethodType):
            callback = WeakMethod(callback)
        self._callback = callback

    def send(self, object_id, action, content):
        """ Send the action to any attached listeners.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        self.messagePosted.emit(object_id, action, content)

    def receive(self, object_id, action, content):
        """ Receive a message sent to the socket.

        The message will be routed to the registered callback, if one
        exists.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        callback = self._callback
        if callback is not None:
            callback(object_id, action, content)


ActionSocketInterface.register(QActionSocket)


#------------------------------------------------------------------------------
# QClientSocket
#------------------------------------------------------------------------------
class QClientSocket(QActionSocket):
    """ A client-side implementation of QActionSocket.

    """
    # The vanilla QActionSocket is a sufficient implementation.
    pass


#------------------------------------------------------------------------------
# QServerSocket
#------------------------------------------------------------------------------
#: The set of actions which should be batched and sent to the client as
#: a single message. This allows a client to perform intelligent message
#: handling when dealing with messages that may affect the widget tree.
BATCH_ACTIONS = set(['destroy', 'children_changed', 'relayout'])

#: A custom event type used by QDeferredMessageBatch.
TickDown = QEvent.Type(QEvent.registerEventType())


class QDeferredMessageBatch(QObject):
    """ A QObject subclass which aggregates batch messages.

    Each time a message is added to this object, its tick count is
    incremented and a tick down event is posted to the event queue.
    When the object receives the tick down event, it decrements its
    tick count, and if it's zero, fires the `triggered` signal.

    This allows a consumer of the batch to continually add messages and
    have the `triggered` signal fired only when the event queue is fully
    drained of relevant messages.

    """
    #: A signal emitted when the consumer of the batch should process
    #: the messages contained in the batch.
    triggered = Signal()

    def __init__(self):
        """ Initialize a QDeferredMessageBatch.

        """
        super(QDeferredMessageBatch, self).__init__()
        self._messages = []
        self._tick = 0

    def messages(self):
        """ Get the messages belonging to the batch.

        Returns
        -------
        result : list
            The list of messages added to the batch.

        """
        return self._messages

    def addMessage(self, message):
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
            QCoreApplication.postEvent(self, QEvent(TickDown))
        self._tick += 1

    def customEvent(self, event):
        """ Handle custom events posted to this object.

        This will handle events of type TickDown. If the tick count
        reaches zero, the `triggered` signal will be emitted.

        """
        if event.type() == TickDown:
            self._tick -= 1
            if self._tick == 0:
                self.triggered.emit()
            else:
                QCoreApplication.postEvent(self, QEvent(TickDown))


class QServerSocket(QActionSocket):
    """ A server-side implementation of QActionSocket.

    This class adds batching functionality for certain actions which
    should be collapsed and sent to the client as a batch.

    """
    def __init__(self, session_id):
        """ Initialize a QServerSocket.

        session_id : str
            The string identifier to use for sending batched messages
            to the client session.

        """
        super(QServerSocket, self).__init__()
        self._session_id = session_id
        self._batch = None

    def send(self, object_id, action, content):
        """ Send the action to any attached listeners.

        This overrides the parent class method to batch messages with
        certain action types.

        """
        if action in BATCH_ACTIONS:
            batch = self._batch
            if batch is None:
                batch = self._batch = QDeferredMessageBatch()
                batch.triggered.connect(self._onBatchTriggered)
            batch.addMessage((object_id, action, content))
        else:
            super(QServerSocket, self).send(object_id, action, content)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onBatchTriggered(self):
        """ A private handler for the `triggered` signal on the batch.

        """
        batch = self._batch
        self._batch = None
        content = {'batch': batch.messages()}
        self.send(self._session_id, 'message_batch', content)

