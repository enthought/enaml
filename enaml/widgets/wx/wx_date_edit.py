#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime

import wx

from traits.api import implements

from .wx_control import WXControl

from ..date_edit import IDateEditImpl


def _to_wx_date(py_date):
    day = py_date.day
    month = py_date.month - 1 # Thank you wx for being moronic!!!
    year = py_date.year
    return wx.DateTimeFromDMY(day, month, year)


def _from_wx_date(wx_date):
    if wx_date.IsValid():
        day = wx_date.GetDay()
        month = wx_date.GetMonth() + 1 # Thank you wx for being moronic!!!
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
        self.set_date(parent.date)
        min_date = parent.minimum_date
        max_date = parent.maximum_date
        if min_date is not None:
            self.set_minimum_date(min_date)
        if max_date is not None:
            self.set_maximum_date(max_date)
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
        """ Binds the event handlers for the date widget. Not meant
        for public consumption.

        """
        widget = self.widget
        widget.Bind(wx.EVT_DATE_CHANGED, self.on_date_changed)

    def on_date_changed(self, event):
        """ The event handler for the date's changed event. Not meant 
        for public consumption.

        """
        event.Skip()
        date = _from_wx_date(self.widget.GetValue())
        if date:
            self.parent.date = date
            self.parent.activated = date
            
    def set_date(self, date):
        """ Sets the date on the widget with the provided value. Not
        meant for public consumption.

        """
        self.widget.SetValue(_to_wx_date(date))

    def set_minimum_date(self, date):
        """ Sets the minimum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.SetRange(_to_wx_date(date), self.widget.GetUpperLimit())

    def set_maximum_date(self, date):
        """ Sets the maximum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.SetRange(self.widget.GetLowerLimit(), _to_wx_date(date))

