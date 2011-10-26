#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import date_edit

from enaml.widgets.qt.qt_date_edit import qdate_to_python

class TestQtDateEdit(QtTestAssistant, date_edit.TestDateEdit):
    """ QtDateEdit tests. """

    def get_date(self, widget):
        """  Get the toolkits widget's active date.

        """
        date = widget.date()
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

    def change_date(self, widget, date):
        """ Simulate a change date action at the toolkit widget.

        .. note:: The setDate method in Qt will also signal the dateChanged
            signal.
        """
        self.widget.setDate(date)

    def get_date_as_string(self, widget):
        """  Get the toolkits widget's active date as a string.

        """
        return self.widget.text()

