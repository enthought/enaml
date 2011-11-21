#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import calendar

from enaml.widgets.qt.qt_date_edit import qdate_to_python


class TestQtCalendar(QtTestAssistant, calendar.TestCalendar):
    """ QtCalendar tests. 

    """
    def get_date(self, widget):
        """  Get the toolkits widget's active date.

        """
        date = widget.selectedDate()
        return qdate_to_python(date)

    def get_min_date(self, widget):
        """  Get the toolkits widget's maximum date attribute.

        """
        date = widget.minimumDate()
        return qdate_to_python(date)

    def get_max_date(self, widget):
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

        """
        # The setDate method in Qt will also signal the dateSelected 
        # signal.
        widget.setSelectedDate(date)

