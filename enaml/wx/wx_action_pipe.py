#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from enaml.core.object import ActionPipeInterface


#: The event type for posting messages to the application
wxActionPipeEvent, EVT_ACTION_PIPE = wx.lib.newevent.NewEvent()


class wxActionPipe(wx.EvtHandler):
    """ A messaging pipe implementation.

    This is a small wx.EvtHandler subclass which converts a `send` on
    the pipe into an event which is bound to by the WxApplication.

    This object also satisfies the Enaml ActionPipeInterface.

    """
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
        event = wxActionPipeEvent(
            object_id=object_id, action=action, content=content,
        )
        wx.PostEvent(self, event)


ActionPipeInterface.register(wxActionPipe)

