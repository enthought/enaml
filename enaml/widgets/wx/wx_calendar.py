import wx.calendar

from traits.api import implements

from .wx_control import WXControl

from ..calendar import ICalendarImpl


class WXCalendar(WXControl):
    """ A wxPython implementation of Calendar.

    A Calendar displays a Python datetime.date using an wx.CalendarCtrl.
    
    See Also
    --------
    Calendar
    
    """
    implements(ICalendarImpl)

    #---------------------------------------------------------------------------
    # ICalendarImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the wx.calendar.CalendarCtrl.

        """
        self.widget = wx.calendar.CalendarCtrl(self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes of the control.

        """
        parent = self.parent
        self.set_date(parent.date)
        min_date = parent.minimum_date
        max_date = parent.maximum_date
        if min_date is not None:
            self.set_minimum_date(min_date)
        if max_date is not None:
            self.set_maximum_date(max_date)
        self.widget.SetMinSize(parent.get_style('size_hint'))
        self.bind()

    def parent_date_changed(self, date):
        """ The change handler for the 'date' attribute. Not meant for
        public consumption.

        """
        self.set_date(date)

    def parent_minimum_date_changed(self, date):
        """ The change handler for the 'minimum_date' attribute. Not 
        meant for public consumption.

        """
        self.set_minimum_date(date)

    def parent_maximum_date_changed(self, date):
        """ The change handler for the 'maximum_date' attribute. Not
        meant for public consumption.

        """
        self.set_maximum_date(date)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the calendar widget. Not meant
        for public consumption.

        """
        widget = self.widget
        widget.Bind(wx.calendar.EVT_CALENDAR, self.on_date_selected)
        widget.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.on_sel_changed)

    def on_date_selected(self, event):
        """ The event handler for the calendar's activation event. Not
        meant for public consumption.

        """
        date = self.widget.PyGetDate()
        self.parent.date = date
        self.parent.activated = date

    def on_sel_changed(self, event):
        """ The event handler for the calendar's selection event. Not
        meant for public consumption.

        """
        date = self.widget.PyGetDate()
        self.parent.selected = date
        
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

