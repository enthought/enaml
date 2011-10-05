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
        self.set_and_validate_date()
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
        self.set_and_validate_date()
        self.parent.selected = self.get_date()

    def parent_minimum_date_changed(self, date):
        """ The change handler for the 'minimum_date' attribute.

        """
        self.set_minimum_date(date)

    def parent_maximum_date_changed(self, date):
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
        parent = self.parent
        date = self.get_date()
        parent.date = date

    def set_and_validate_date(self):
        """ Sets and validates the component date on the widget.

        The method sets the date in the toolkit widget and makes sure that
        the enaml component is syncronized without firing trait notification
        events.It simulates the QtDateEdit behaviour and perfoms the date
        validation in place because the wxPython calendar is not perfoming
        it when date is set programmatically.

        """
        parent = self.parent
        date = parent.date
        validated_date = self.fit_to_range(date)
        if self.get_date != validated_date:
            self.widget.PySetDate(validated_date)
        if validated_date != date:
            self.parent.trait_setq(date=validated_date)



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

    def fit_to_range(self, date):
        """ Fit the date to the component range.

        """
        parent = self.parent
        minimum = parent.minimum_date
        maximum = parent.maximum_date

        date = max(date, minimum)
        date = min(date, maximum)
        return date