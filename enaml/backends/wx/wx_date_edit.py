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
    month = py_date.month - 1  # wx peculiarity!
    year = py_date.year
    return wx.DateTimeFromDMY(day, month, year)


def from_wx_date(wx_date):
    if wx_date.IsValid():
        day = wx_date.GetDay()
        month = wx_date.GetMonth() + 1  # wx peculiarity!
        year = wx_date.GetYear()
        return datetime.date(year, month, day)


class WXDateEdit(WXBoundedDate, AbstractTkDateEdit):
    """ A WX implementation of DateEdit.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.DatePickerCtrl.

        """
        self.widget = wx.DatePickerCtrl(parent)

    def initialize(self):
        """ Initializes the attributes of the control.

        """
        super(WXDateEdit, self).initialize()
        self.set_format(self.shell_obj.date_format)

    def bind(self):
        """ Binds the event handlers for the date widget.

        """
        super(WXDateEdit, self).bind()
        self.widget.Bind(wx.EVT_DATE_CHANGED, self.on_date_changed)

    #--------------------------------------------------------------------------
    # Component attribute notifiers
    #--------------------------------------------------------------------------
    def shell_date_format_changed(self, date_format):
        """ The change handler for the 'format' attribute.

        """
        self.set_format(date_format)

    #--------------------------------------------------------------------------
    # Signal handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self, event):
        """ The event handler for the date's changed event.

        """
        new_date = from_wx_date(event.GetDate())
        self.shell_obj.date = new_date
        self.shell_obj.date_changed(new_date)

    #--------------------------------------------------------------------------
    # Private methods
    #--------------------------------------------------------------------------
    def set_date(self, date):
        """ Sets the date on the widget.

        """
        # wx will not fire an EVT_DATE_CHANGED when setting the
        # value, so we do not need any feeback guards here.
        self.widget.SetValue(to_wx_date(date))

    def set_min_date(self, date):
        """ Sets the minimum date on the widget with the provided value.

        """
        widget = self.widget
        widget.SetRange(to_wx_date(date), widget.GetUpperLimit())

    def set_max_date(self, date):
        """ Sets the maximum date on the widget with the provided value.

        """
        widget = self.widget
        widget.SetRange(widget.GetLowerLimit(), to_wx_date(date))

    def set_format(self, date_format):
        """ Sets the display format on the widget with the provided value.

        .. note:: Changing the format on wx is not supported.
                  See http://trac.wxwidgets.org/ticket/10988

        """
        pass

