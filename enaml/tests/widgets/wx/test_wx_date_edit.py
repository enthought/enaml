#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from enaml.widgets.wx.wx_date_edit import to_wx_date, from_wx_date

from .wx_test_assistant import WXTestAssistant, skip_nonwindows
from .. import date_edit


@skip_nonwindows
class TestWXDateEdit(WXTestAssistant, date_edit.TestDateEdit):
    """ WXDateEdit tests. """

    def test_set_format(self):
        """ Test setting the output format

        """
        self.skipTest('Seetting the display format is not supported in'
                      ' native wxWidgets')

    def get_date(self, widget):
        """  Get the toolkits widget's active date.

        """
        date = widget.GetValue()
        return from_wx_date(date)

    def get_min_date(self, widget):
        """  Get the toolkits widget's maximum date attribute.

        """
        date = widget.GetLowerLimit()
        return from_wx_date(date)

    def get_max_date(self, widget):
        """ Get the toolkits widget's minimum date attribute.

        """
        date = widget.GetUpperLimit()
        return from_wx_date(date)

    def change_date(self, widget, date):
        """ Simulate a change date action at the toolkit widget.

        """
        wx_date = to_wx_date(date)
        widget.SetValue(wx_date)
        event_type = wx.EVT_DATE_CHANGED
        event = wx.DateEvent(widget, wx_date, event_type.typeId)
        widget.GetEventHandler().ProcessEvent(event)
        self.process_wx_events(self.app)

    def get_date_as_string(self, widget):
        """  Get the toolkits widget's active date as a string.

        """
        self.skipTest("The retrival of the date as string is not"
                      "implemented yet for the wx_toolkit")

