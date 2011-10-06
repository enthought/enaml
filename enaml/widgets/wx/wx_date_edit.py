#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime

import wx

from traits.api import implements

from .wx_control import WXControl
from ..date_edit import IDateEditImpl


def to_wx_date(py_date):
    day = py_date.day
    month = py_date.month - 1 # wx peculiarity!
    year = py_date.year
    return wx.DateTimeFromDMY(day, month, year)


def from_wx_date(wx_date):
    if wx_date.IsValid():
        day = wx_date.GetDay()
        month = wx_date.GetMonth() + 1 # wx peculiarity!
        year = wx_date.GetYear()
        return datetime.date(year, month, day)


class WXDateEdit(WXControl):

    implements(IDateEditImpl)

    #---------------------------------------------------------------------------
    # IDateEditImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = wx.DatePickerCtrl(self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes of the control.

        """
        parent = self.parent
        self.set_minimum_date(parent.minimum_date)
        self.set_maximum_date(parent.maximum_date)
        self.set_and_validate_date()
##        self.set_format(parent.format)
        self.bind()

    def parent_date_changed(self, date):
        """ The change handler for the 'date' attribute.

        """
        self.set_and_validate_date()
        self.parent.date_changed = self.get_date()

    def parent_minimum_date_changed(self, date):
        """ The change handler for the 'minimum_date' attribute.

        """
        self.set_minimum_date(date)

    def parent_maximum_date_changed(self, date):
        """ The change handler for the 'maximum_date' attribute.

        """
        self.set_maximum_date(date)


    def parent_format_changed(self, date_format):
        """ The change handler for the 'format' attribute.

        Not implemented in wxPython

        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def bind(self):
        """ Binds the event handlers for the date widget. Not meant
        for public consumption.

        """
        widget = self.widget
        widget.Bind(wx.EVT_DATE_CHANGED, self.on_date_changed)

    def on_date_changed(self, event):
        """ The event handler for the date's changed event. Not meant
        for public consumption.

        """
        parent = self.parent
        parent.date = from_wx_date(event.GetDate())

    def set_and_validate_date(self):
        """ Sets and validates the component date on the widget.

        The method sets the date in the toolkit widget and makes sure that
        the enaml component is syncronized without firing trait notification
        events.It simulates the QtDateEdit behaviour and perfoms the date
        validation in place to avoid exceptions raised by the wxPython
        DatePickerCtrl widget.

        """
        parent = self.parent
        date = parent.date
        validated_date = self.fit_to_range(date)
        self.widget.SetValue(to_wx_date(validated_date))
        if validated_date != date:
            self.parent.trait_setq(date=validated_date)

    def set_minimum_date(self, date):
        """ Sets the minimum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.SetRange(to_wx_date(date), self.widget.GetUpperLimit())

    def set_maximum_date(self, date):
        """ Sets the maximum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.SetRange(self.widget.GetLowerLimit(), to_wx_date(date))

    def get_date(self):
        """ Get the active widget date.

        """
        wx_date = self.widget.GetValue()
        return from_wx_date(wx_date)

    def fit_to_range(self, date):
        """ Fit the date to the component range.

        """
        parent = self.parent
        minimum = parent.minimum_date
        maximum = parent.maximum_date

        date = max(date, minimum)
        date = min(date, maximum)
        return date