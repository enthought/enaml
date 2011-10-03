#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

def process_wx_events(app):
    """ Process posted wxPython events.

    """
    app.ProcessPendingEvents()

def send_wx_event(widget, event_type):
    """ Send a wxPython widget an event (e.g., EVT_BUTTON).

    """
    event = wx.PyCommandEvent(event_type.typeId, widget.GetId())
    widget.GetEventHandler().ProcessEvent(event)

def send_wx_mouse_event(widget, event_type, position=None):
    """ Send a wxPython widget an mouse event (e.g., EVT_BUTTON).

    """
    event = wx.MouseEvent(event_type.typeId)
    if position is None:
        event.m_x = 0
        event.m_y = 0
    else:
        event.m_x = position.x
        event.m_y = position.y
    widget.GetEventHandler().ProcessEvent(event)
