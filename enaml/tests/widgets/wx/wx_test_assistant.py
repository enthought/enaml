#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
from enaml.toolkit import wx_toolkit

class WXTestAssistant(object):
    """ Assistant class for testing wx based components.

    This class is to be used as a mixing aling with the base enaml test case
    class for the components tests of the wx backend. It sets the correct
    toolkit attribute and provides some useful methods to mock events in
    wx.

    """

    toolkit = wx_toolkit()

    def process_wx_events(self, app):
        """ Process posted wxPython events.

        """
        app.ProcessPendingEvents()

    def send_wx_event(self, widget, event_type):
        """ Send a wxPython widget an event (e.g., EVT_BUTTON).

        """
        event = wx.PyCommandEvent(event_type.typeId, widget.GetId())
        widget.GetEventHandler().ProcessEvent(event)

    def send_wx_mouse_event(self, widget, event_type, position=None):
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
