#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
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
        self.widget = widget = wx.calendar.CalendarCtrl(self.parent_widget())
        widget.SetDoubleBuffered(True)

    def initialize_widget(self):
        """ Initializes the attributes of the control.

        """
        parent = self.parent
        self.set_minimum_date(parent.minimum_date)
        self.set_maximum_date(parent.maximum_date)
        self.set_date(parent.date)
        self.bind()

    def create_style_handler(self):
        # XXX Calendar doesn't handle null color background properly
        # so for now we just don't let the parent class set the color.
        pass

    def initialize_style(self):
        # XXX Calendar doesn't handle null color background properly
        # so for now we just don't let the parent class set the color.
        pass

    def parent_date_changed(self, date):
        """ The change handler for the 'date' attribute.

        """
        old_widget_date = self.get_date()
        self.set_date(date)
        if old_widget_date != date:
            self.parent.selected = date


    def parent__minimum_date_changed(self, date):
        """ The change handler for the 'minimum_date' attribute.

        """
        self.set_minimum_date(date)

    def parent__maximum_date_changed(self, date):
        """ The change handler for the 'maximum_date' attribute.

        """
        self.set_maximum_date(date)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the calendar widget.

        """
        widget = self.widget
        widget.Bind(wx.calendar.EVT_CALENDAR, self.on_date_activated)
        widget.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.on_selection_changed)

    def on_date_activated(self, event):
        """ The event handler for the calendar's activation event.

        """
        date = self.get_date()
        self.parent.date = date
        self.parent.activated = date

    def on_selection_changed(self, event):
        """ The event handler for the calendar's selection event.

        """
        date = self.get_date()
        self.parent.selected = date

    def set_date(self, date):
        """ Sets the component date on the widget.

        """
        self.widget.PySetDate(date)


    def set_minimum_date(self, date):
        """ Sets the minimum date on the widget with the provided value.

        """
        self.widget.PySetLowerDateLimit(date)

    def set_maximum_date(self, date):
        """ Sets the maximum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.PySetUpperDateLimit(date)

    def get_date(self):
        """ Get the active widget date.

        """
        return self.widget.PyGetDate()
