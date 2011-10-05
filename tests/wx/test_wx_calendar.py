#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx.calendar

from .. import calendar
from enaml.toolkit import wx_toolkit


class TestWxCalendar(calendar.TestCalendar):
    """ WXCalendar tests. """

    toolkit = wx_toolkit()

    def get_date(self, widget):
        """ Get a calendar's active date.

        """
        return widget.PyGetDate()

    def get_minimum_date(self, widget):
        """ Get a calendar's minimum date attribute.

        """
        return widget.PyGetLowerDateLimit()

    def get_maximum_date(self, widget):
        """ Get a calendar's maximum date attribute.
        
        """
        return widget.PyGetUpperDateLimit()

    def activate_date(self, widget, date):
        """ Fire an event to indicate that a date was activated.
        
        """
        cal_event = wx.calendar.EVT_CALENDAR
        event = wx.calendar.CalendarEvent(widget, cal_event.typeId)
        event.PySetDate(date)
        widget.GetEventHandler().ProcessEvent(event)
        
    def select_date(self, widget, date):
        """ Fire an event to indicate that a date was selected.
        
        """
        cal_select_event = wx.calendar.EVT_CALENDAR_SEL_CHANGED
        event = wx.calendar.CalendarEvent(widget, cal_select_event.typeId)
        widget.PySetDate(date)
        event.PySetDate(date)
        widget.GetEventHandler().ProcessEvent(event)
