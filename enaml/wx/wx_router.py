#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.utils import log_exceptions

import wx
import wx.lib.newevent


#: The event type for posting messages to the application
wxAppMessageEvent, EVT_APP_MESSAGE = wx.lib.newevent.NewEvent()

#: The event type for posting messages to the client
wxClientMessageEvent, EVT_CLIENT_MESSAGE = wx.lib.newevent.NewEvent()

#: The event type for posting callback messages
wxCallbackMessageEvent, EVT_CALLBACK_MESSAGE = wx.lib.newevent.NewEvent()


class wxRouter(wx.EvtHandler):
    """ A simple wx.EvtHandler subclass which assists in routing 
    messages in a deferred fashion.

    This object emits three events:


    """
    def __init__(self):
        """ Initialize a wxRouter.

        """
        super(wxRouter, self).__init__()
        self.Bind(EVT_CALLBACK_MESSAGE, self._OnCallbackMessage)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    @log_exceptions
    def _OnCallbackMessage(self, event):
        """ The event handler for the EVT_CALLBACK_MESSAGE event.

        This handler will invoke the passed callback. Exceptions raised 
        in the callback will generate an error log.

        Parameters
        ----------
        event : wxCallbackMessageEvent
            The callback message event which contains the necessary 
            callback data.
            
        """
        callback = event.callback
        args = event.args
        kwargs = event.kwargs
        callback(*args, **kwargs)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def AddCallback(self, callback, *args, **kwargs):
        """ Add the callback to the queue to be run in the future.

        Parameters
        ----------
        callback : callable
            The callable to be run at some point in the future.

        *args, **kwargs
            The positional and keyword arguments to pass to the 
            callable when it is invoked.

        """
        event = wxCallbackMessageEvent(
            callback=callback, args=args, kwargs=kwargs
        )
        wx.PostEvent(self, event)

    def PostClientMessage(self, message):
        """ Post a deferred message to be delivered to the client.

        Parameters
        ----------
        message : Message
            The Message object to send to the client.

        """
        event = wxClientMessageEvent(message=message)
        wx.PostEvent(self, event)

    def PostAppMessage(self, message):
        """ Post a deferred message to be delivered to the application.

        Parameters
        ----------
        message : Message
            The Message object to send to the client.

        """
        event = wxAppMessageEvent(message=message)
        wx.PostEvent(self, event)

