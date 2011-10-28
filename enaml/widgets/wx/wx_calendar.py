#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx.calendar

from .wx_bounded_date import WXBoundedDate
from ..calendar import AbstractTkCalendar


class WXCalendar(WXBoundedDate, AbstractTkCalendar):
    """ A wxPython implementation of Calendar.

    A Calendar displays a Python datetime.date using an wx.CalendarCtrl.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the wx.calendar.CalendarCtrl.

        """
        self.widget = widget = wx.calendar.CalendarCtrl(self.parent_widget())
        widget.SetDoubleBuffered(True)

    def bind(self):
        """ Binds the event handlers for the calendar widget.

        """
        super(WXCalendar, self).bind()
        widget = self.widget
        widget.Bind(wx.calendar.EVT_CALENDAR, self.on_date_activated)
        widget.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED,
                    self.on_date_selected)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------

    def on_date_activated(self, event):
        """ The event handler for the calendar's activation event.

        """
        shell = self.shell_obj
        widget = self.widget
        date = widget.PyGetDate()
        shell.date = date
        shell.activated = date

    def on_date_selected(self, event):
        """ The event handler for the calendar's selection event.

        """
        shell = self.shell_obj
        widget = self.widget
        date = widget.PyGetDate()
        shell.selected = date

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def set_date(self, date, events=True):
        """ Sets the component date on the widget.

        wxCalendar will not fire an EVT_CALENDAR_SEL_CHANGED event when
        the value is programmatically set, so the method fires the
        `selected` event manually after setting the value in the widget.

        """
        widget = self.widget
        widget.PySetDate(date)
        if events:
            shell = self.shell_obj
            shell.selected = date


    def set_min_date(self, date):
        """ Sets the minimum date on the widget with the provided value.

        """
        widget = self.widget
        widget.PySetLowerDateLimit(date)

    def set_max_date(self, date):
        """ Sets the maximum date on the widget with the provided value.

        """
        widget = self.widget
        widget.PySetUpperDateLimit(date)
