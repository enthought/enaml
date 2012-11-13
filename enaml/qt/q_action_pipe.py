#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.core.object import ActionPipeInterface

from .qt.QtCore import QObject, Signal, QEvent, QCoreApplication


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


class QActionPipe(QObject):
    """ A messaging pipe implementation.

    This is a small QObject subclass which converts a `send` on the pipe
    into a signal which is connected to by the QtApplication.

    This object also satisfies the Enaml ActionPipeInterface.

    """
    #: A signal emitted when an item has been sent down the pipe.
    actionPosted = Signal(object, object, object)

    def __init__(self, *args, **kwargs):
        """ Initialize a QActionPipe.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QObject.

        """
        super(QActionPipe, self).__init__(*args, **kwargs)
        self._batch = None

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
        if action in BATCH_ACTIONS:
            batch = self._batch
            if batch is None:
                batch = self._batch = QDeferredMessageBatch()
                batch.triggered.connect(self._onBatchTriggered)
            batch.addMessage((object_id, action, content))
        else:
            self.actionPosted.emit(object_id, action, content)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onBatchTriggered(self):
        """ A private handler for the `triggered` signal on the
        QDeferredMessageBatch.

        """
        batch = self._batch
        self._batch = None
        self.send('', 'message_batch', {'batch': batch.messages()})


ActionPipeInterface.register(QActionPipe)

