#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from enaml.core.object import ActionPipeInterface


#: The set of actions which should be batched and sent to the client as
#: a single message. This allows a client to perform intelligent message
#: handling when dealing with messages that may affect the widget tree.
BATCH_ACTIONS = set(['destroy', 'children_changed', 'relayout'])


#: A custom event type for posting messages to the application.
wxActionPipeEvent, EVT_ACTION_PIPE = wx.lib.newevent.NewEvent()


#: A custom event type for ticking down the message batch.
wxTickDownEvent, EVT_TICK_DOWN = wx.lib.newevent.NewEvent()


#: A custom event type for triggering the message batch.
wxBatchTriggeredEvent, EVT_BATCH_TRIGGERED = wx.lib.newevent.NewEvent()


class wxDeferredMessageBatch(wx.EvtHandler):
    """ A wxEvtHandler subclass which aggregates batch messages.

    Each time a message is added to this object, its tick count is
    incremented and a tick down event is posted to the event queue.
    When the object receives the tick down event, it decrements its
    tick count, and if it's zero, emits an EVT_BATCH_TRIGGERED event.

    This allows a consumer of the batch to continually add messages and
    have the trigger event fired only when the event queue is fully
    drained of relevant messages.

    """
    def __init__(self):
        """ Initialize a wxDeferredMessageBatch.

        """
        super(wxDeferredMessageBatch, self).__init__()
        self._messages = []
        self._tick = 0
        self.Bind(EVT_TICK_DOWN, self.OnTickDown)

    def GetMessages(self):
        """ Get the messages belonging to the batch.

        Returns
        -------
        result : list
            The list of messages added to the batch.

        """
        return self._messages

    def AddMessage(self, message):
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
            wx.PostEvent(self, wxTickDownEvent())
        self._tick += 1

    def OnTickDown(self, event):
        """ Handle tick down events posted to this object.

        This will handle events of type wxTickDownEvent. If the tick
        count reaches zero, an EVT_BATCH_TRIGGERED event will be sent.

        """
        self._tick -= 1
        if self._tick == 0:
            self.ProcessEvent(wxBatchTriggeredEvent())
        else:
            wx.PostEvent(self, wxTickDownEvent())


class wxActionPipe(wx.EvtHandler):
    """ A messaging pipe implementation.

    This is a small wx.EvtHandler subclass which converts a `send` on
    the pipe into an event which is bound to by the WxApplication.

    This object also satisfies the Enaml ActionPipeInterface.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxActionPipe.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wxEvtHandler.

        """
        super(wxActionPipe, self).__init__(*args, **kwargs)
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
                batch = self._batch = wxDeferredMessageBatch()
                batch.Bind(EVT_BATCH_TRIGGERED, self._OnBatchTriggered)
            batch.AddMessage((object_id, action, content))
        else:
            event = wxActionPipeEvent(
                object_id=object_id, action=action, content=content,
            )
            wx.PostEvent(self, event)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _OnBatchTriggered(self, event):
        """ A private handler for the EVT_BATCH_TRIGGERED event sent by
        the wxDeferredMessageBatch.

        """
        batch = self._batch
        self._batch = None
        self.send('', 'message_batch', {'batch': batch.GetMessages()})


ActionPipeInterface.register(wxActionPipe)

