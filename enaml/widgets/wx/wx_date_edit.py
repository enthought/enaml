#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime

import wx

from .wx_bounded_date import WXBoundedDate
from ..date_edit import AbstractTkDateEdit

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


class WXDateEdit(WXBoundedDate, AbstractTkDateEdit):
    """ A WX implementation of DateEdit.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        self.widget = wx.DatePickerCtrl(self.parent_widget())

    def initialize(self):
        """ Initializes the attributes of the control.

        """
        super(WXDateEdit, self).initialize()
        # FIXME: Set the date format functionality is not available yet
        shell = self.shell_obj
        self.set_format(shell.date_format)

    def bind(self):
        """ Binds the event handlers for the date widget.

        """
        super(WXDateEdit, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_DATE_CHANGED, self.on_date_changed)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_date_format_changed(self, date_format):
        """ The change handler for the 'format' attribute.

        .. note:: Currently this call is ignored

        """
        self.set_format(date_format)
##        self.shell_obj.size_hint_updated = True

    def on_date_changed(self, event):
        """ The event handler for the date's changed event. Not meant
        for public consumption.

        """
        shell = self.shell_obj
        shell.date = from_wx_date(event.GetDate())

    def set_date(self, date, events=True):
        """ Sets the date on the widget.

        wxDatePickerCtrl will not fire an EVT_DATE_CHANGED event when
        the value is programmatically set, so the method fires the
        `date_changed` event manually after setting the value in the
        widget.

        """
        widget = self.widget
        widget.SetValue(to_wx_date(date))
        if events:
            shell = self.shell_obj
            shell.date_changed = date

    def set_min_date(self, date):
        """ Sets the minimum date on the widget with the provided value.
        Not meant for public consumption.

        """
        widget = self.widget
        widget.SetRange(to_wx_date(date), widget.GetUpperLimit())

    def set_max_date(self, date):
        """ Sets the maximum date on the widget with the provided value.
        Not meant for public consumption.

        """
        widget = self.widget
        widget.SetRange(widget.GetLowerLimit(), to_wx_date(date))

    def set_format(self, date_format):
        pass
