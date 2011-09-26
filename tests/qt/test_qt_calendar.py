#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..common import calendar
from enaml.toolkit import qt_toolkit


class TestQtCalendar(calendar.TestCalendar):
    """ QtCalendar tests. """

    toolkit = qt_toolkit()

    def get_date(self, widget):
        """ Get a calendar's active date.

        """
        return widget.selectedDate()

    def get_minimum_date(self, widget):
        """ Get a calendar's minimum date attribute.

        """
        return widget.minimumDate()

    def get_maximum_date(self, widget):
        """ Get a calendar's maximum date attribute.
        
        """
        return widget.maximumDate()

    def activate_date(self, widget, date):
        """ Fire an event to indicate that a date was activated.
        
        """
        widget.activated.emit(date)
        
    def select_date(self, widget, date):
        """ Fire an event to indicate that a date was selected.
        
        """
        widget.setSelectedDate(date)
        widget.selectionChanged.emit()
