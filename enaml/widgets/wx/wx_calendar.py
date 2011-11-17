#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from wx.calendar import CalendarCtrl, EVT_CALENDAR, EVT_CALENDAR_SEL_CHANGED

from .wx_bounded_date import WXBoundedDate

from ..calendar import AbstractTkCalendar


class WXCalendar(WXBoundedDate, AbstractTkCalendar):
    """ A wxPython implementation of Calendar.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the wx.calendar.CalendarCtrl.

        """
        self.widget = CalendarCtrl(self.parent_widget())

    def bind(self):
        """ Binds the event handlers for the calendar widget.

        """
        super(WXCalendar, self).bind()
        widget = self.widget
        widget.Bind(EVT_CALENDAR, self._on_date_activated)
        widget.Bind(EVT_CALENDAR_SEL_CHANGED, self._on_date_selected)

    #--------------------------------------------------------------------------
    # Signal handlers
    #--------------------------------------------------------------------------
    def _on_date_activated(self, event):
        """ The event handler for the calendar's activation event.

        """
        shell = self.shell_obj
        date = self.widget.PyGetDate()
        shell.date = date
        shell.activated = date

    def _on_date_selected(self, event):
        """ The event handler for the calendar's selection event.

        """
        self.shell_obj.selected = event.PyGetDate()

    #---------------------------------------------------------------------------
    # Private methods
    #---------------------------------------------------------------------------
    def _set_date(self, date):
        """ Sets the component date in the widget.

        """
        # wx does not emit a selection changed event when manually 
        # setting the date, so we don't need a feedback guard here.
        self.widget.PySetDate(date)

    def _set_min_date(self, date):
        """ Sets the minimum date on the widget with the provided value.

        """
        self.widget.PySetLowerDateLimit(date)

    def _set_max_date(self, date):
        """ Sets the maximum date on the widget with the provided value.

        """
        self.widget.PySetUpperDateLimit(date)

