#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant

from .. import datetime_edit

from enaml.widgets.qt.qt_datetime_edit import qdatetime_to_python


class TestQtDatetimeEdit(QtTestAssistant, datetime_edit.TestDatetimeEdit):
    """ QtDateEdit tests. 

    """
    def get_datetime(self, widget):
        """  Get the toolkits widget's active datetime.

        """
        datetime = widget.dateTime()
        return qdatetime_to_python(datetime)

    def get_min_datetime(self, widget):
        """  Get the toolkits widget's maximum datetime attribute.

        """
        datetime = widget.minimumDateTime()
        return qdatetime_to_python(datetime)

    def get_max_datetime(self, widget):
        """ Get the toolkits widget's minimum datetime attribute.

        """
        datetime = widget.maximumDateTime()
        return qdatetime_to_python(datetime)

    def change_datetime(self, widget, datetime):
        """ Simulate a change datetime action at the toolkit widget.

        """
        # The setDateTime method in Qt will also emit the
        # dateTimeChanged signal.
        self.widget.setDateTime(datetime)

    def get_datetime_as_string(self, widget):
        """  Get the toolkits widget's active datetime as a string.

        """
        return self.widget.text()

