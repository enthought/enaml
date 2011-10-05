#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .. import calendar
from enaml.toolkit import qt_toolkit

from enaml.widgets.qt.qt_date_edit import qdate_to_python

class TestQtCalendar(calendar.TestCalendar):
    """ QtCalendar tests. """

    toolkit = qt_toolkit()

    def get_date(self, widget):
        """  Get the toolkits widget's active date.

        """
        date = widget.selectedDate()
        return qdate_to_python(date)

    def get_minimum_date(self, widget):
        """  Get the toolkits widget's maximum date attribute.

        """
        date = widget.minimumDate()
        return qdate_to_python(date)

    def get_maximum_date(self, widget):
        """ Get the toolkits widget's minimum date attribute.

        """
        date = widget.maximumDate()
        return qdate_to_python(date)

    def activate_date(self, widget, date):
        """ Fire an event to indicate that a date was activated.

        """
        widget.activated.emit(date)

    def select_date(self, widget, date):
        """ Fire an event to indicate that a date was selected.

        .. note:: The setDate method in Qt will also signal the dateSelected
            signal.

        """
        widget.setSelectedDate(date)
