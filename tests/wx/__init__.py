#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

def send_wx_event(widget, event_type):
    """ Send a wxPython widget an event (e.g., EVT_BUTTON).
    
    """
    event = wx.PyCommandEvent(event_type.typeId, widget.GetId())
    widget.GetEventHandler().ProcessEvent(event)
