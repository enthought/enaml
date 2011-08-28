from datetime import date
from calendar import monthrange

import wx.calendar

from traits.api import implements, Date, Event

from .wx_element import WXElement

from ..i_calendar import ICalendar


class WXCalendar(WXElement):
    """ A calendar widget.

    A Calendar displays a Python datetime.date using an appropriate
    toolkit specific control. The date attribute is synchronized 
    bi-directionally with the day, month, and year attributes.
    
    Attributes
    ----------
    date : Date
        The currently selected date.
    
    day : Int
        The selected day.
    
    month : Int
        The selected month.
    
    year : Int
        The selected year.
    
    """
    implements(ICalendar)

    #===========================================================================
    # ICalendar interface
    #===========================================================================
    date = Date(date.today())

    minimum_date = Date

    maximum_date = Date

    selected = Event

    activated = Event

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates and binds a wx.calendar.CalendarCtrl.

        """
        widget = wx.calendar.CalendarCtrl(self.parent_widget())
        widget.Bind(wx.calendar.EVT_CALENDAR, self._on_date_selected)
        widget.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self._on_sel_changed)
        self.widget = widget

    def init_attributes(self):
        """ Sync the widget's display with the date trait.

        Default to today if no date is specified.

        """
        self.set_date(self.date)
        min_date = self.minimum_date
        max_date = self.maximum_date
        if min_date is not None:
            self.set_minimum_date(min_date)
        if max_date is not None:
            self.set_maximum_date(max_date)
        
    def init_meta_handlers(self):
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _date_changed(self, date):
        """ The change handler for the 'date' attribute.

        """
        self.set_date(date)

    def _minimum_date_changed(self, date):
        """ The change handler for the 'minimum_date' attribute.

        """
        self.set_minimum_date(date)

    def _maximum_date_changed(self, date):
        """ The change handler for the 'maximum_date' attribute.

        """
        self.set_maximum_date(date)

    #---------------------------------------------------------------------------
    # Event handlers
    #---------------------------------------------------------------------------
    def _on_date_selected(self, event):
        """ The event handler for the calendar's activation event.

        """
        date = self.widget.PyGetDate()
        self.date = date
        self.activated = date
        event.Skip()

    def _on_sel_changed(self, event):
        """ The event handler for the calendar's selection event.

        """
        date = self.widget.PyGetDate()
        self.selected = date
        event.Skip()
        
    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_date(self, date):
        """ Sets the date on the widget with the provided value.

        """
        self.widget.PySetDate(date)

    def set_minimum_date(self, date):
        """ Sets the minimum date on the widget with the provided value.

        """
        self.widget.PySetLowerDateLimit(date)

    def set_maximum_date(self, date):
        """ Sets the maximum date on the widget with the provided value.

        """
        self.widget.PySetUpperDateLimit(date)

