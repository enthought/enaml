import wx.calendar

from datetime import date
from calendar import monthrange

from traits.api import implements, Date, Int

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

    #--------------------------------------------------------------------------
    # ICalendar interface
    #--------------------------------------------------------------------------
    date = Date

    day = Int

    month = Int

    year = Int


    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def create_widget(self, parent):
        """ Creates and binds a wx.calendar.CalendarCtrl.

        """
        widget = wx.calendar.CalendarCtrl(parent.widget)
        widget.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self._on_date_selected)
        widget.Bind(wx.calendar.EVT_CALENDAR_DAY, self._on_day_selected)
        widget.Bind(wx.calendar.EVT_CALENDAR_MONTH, self._on_month_selected)
        widget.Bind(wx.calendar.EVT_CALENDAR_YEAR, self._on_year_selected)
        self.widget = widget

    def init_attributes(self):
        """ Sync the widget's display with the date trait.

        Default to today if no date is specified.

        """
        if not self.date:
            self.date = date.today()
        self.widget.PySetDate(self.date)
        

    def init_meta_handlers(self):
        pass

    def _date_changed(self):
        """ Sync the widget and day, month, and year traits with the date trait.

        """
        self.widget.PySetDate(self.date)
        
        today = self.date
        self.day = today.day
        self.month = today.month
        self.year = today.year

    def _day_changed(self):
        if self.date.day != self.day:
            self._set_pydate()

    def _month_changed(self):
        if self.date.month != self.month:
            self._set_pydate()

    def _year_changed(self):
        if self.date.year != self.year:
            self._set_pydate()

    def _on_date_selected(self, event):
        today = self.widget.PyGetDate()
        if self.date != today:
            self.date = today
    
    def _on_day_selected(self, event):
        pass
    
    def _on_month_selected(self, event):
        pass


    def _on_year_selected(self, event):
        pass

    def _set_pydate(self):
        """ Set the date trait with the year, month, and day values.

        """
        self.date = date(self.year, self.month, self.day)