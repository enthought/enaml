from datetime import date

import wx.calendar

from traits.api import implements, Date, Event

from .wx_element import WXElement

from ..i_calendar import ICalendar


class WXCalendar(WXElement):
    """ A wxPython implementation of ICalendar.

    A Calendar displays a Python datetime.date using an wx CalendarCtrl.
    
    See Also
    --------
    ICalendar
    
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

        This is called by the 'layout' method of WXElement and is not
        meant for public consumption.

        """
        widget = wx.calendar.CalendarCtrl(self.parent_widget())
        widget.Bind(wx.calendar.EVT_CALENDAR, self._on_date_selected)
        widget.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self._on_sel_changed)
        self.widget = widget

    def init_attributes(self):
        """ Initializes the attributes of the control.

        This is called by the 'layout' method of WXElement and is not
        meant for public consumption.

        """
        self.set_date(self.date)
        min_date = self.minimum_date
        max_date = self.maximum_date
        if min_date is not None:
            self.set_minimum_date(min_date)
        if max_date is not None:
            self.set_maximum_date(max_date)
        
    def init_meta_handlers(self):
        """ Initializes the meta handlers of the control.

        This is called by the 'layout' method of WXElement and is not
        meant for public consumption.

        """
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _date_changed(self, date):
        """ The change handler for the 'date' attribute. Not meant for
        public consumption.

        """
        self.set_date(date)

    def _minimum_date_changed(self, date):
        """ The change handler for the 'minimum_date' attribute. Not 
        meant for public consumption.

        """
        self.set_minimum_date(date)

    def _maximum_date_changed(self, date):
        """ The change handler for the 'maximum_date' attribute. Not
        meant for public consumption.

        """
        self.set_maximum_date(date)

    #---------------------------------------------------------------------------
    # Event handlers
    #---------------------------------------------------------------------------
    def _on_date_selected(self, event):
        """ The event handler for the calendar's activation event. Not
        meant for public consumption.

        """
        date = self.widget.PyGetDate()
        self.date = date
        self.activated = date
        event.Skip()

    def _on_sel_changed(self, event):
        """ The event handler for the calendar's selection event. Not
        meant for public consumption.

        """
        date = self.widget.PyGetDate()
        self.selected = date
        event.Skip()
        
    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_date(self, date):
        """ Sets the date on the widget with the provided value. Not
        meant for public consumption.

        """
        self.widget.PySetDate(date)

    def set_minimum_date(self, date):
        """ Sets the minimum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.PySetLowerDateLimit(date)

    def set_maximum_date(self, date):
        """ Sets the maximum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.PySetUpperDateLimit(date)

