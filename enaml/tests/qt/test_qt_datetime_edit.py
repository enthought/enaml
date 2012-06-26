#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest, datetime
from uuid import uuid4

from enaml.qt.qt import QtCore
from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_datetime_edit import QtDatetimeEdit
from enaml.qt.qt_local_pipe import QtLocalPipe

# Workarounds for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdatetime_to_python = QtCore.QDateTime.toPython
except AttributeError: # pragma: no cover
    qdatetime_to_python = QtCore.QDateTime.toPyDateTime

class TestQtDatetimeEdit(unittest.TestCase):
    """ Unit tests for the QtDatetimeEdit

    """
    def setUp(self):
        """ Set up the widget for testing

        """
        self.datetime_edit = QtDatetimeEdit(None, uuid4().hex, QtLocalPipe(),
                                            QtLocalPipe())
        self.datetime_edit.create()

    def test_set_datetime(self):
        """ Test the QtDatetimeEdit's set_datetime command

        """
        date_time = datetime.datetime(2012,6,22,0,0,0,0)
        self.datetime_edit.recv('set_datetime', {'value':date_time})
        widget_date_time = qdatetime_to_python(self.datetime_edit.widget.dateTime())
        self.assertEqual(widget_date_time, date_time)

    def test_set_min_datetime(self):
        """ Test the QtDatetimeEdit's set_min_datetime command

        """
        min_date_time = datetime.datetime(1752,9,14, 0, 0, 0, 0)
        self.datetime_edit.recv('set_min_datetime', {'value':min_date_time})
        widget_min_date_time = qdatetime_to_python(
            self.datetime_edit.widget.minimumDateTime())
        self.assertEqual(widget_min_date_time, min_date_time)

    def test_set_max_datetime(self):
        """ Test the QtDatetimeEdit's set_max_datetime command

        """
        max_date_time = datetime.datetime(7999, 12, 31, 23, 59, 59, 999000)
        self.datetime_edit.recv('set_max_datetime', {'value':max_date_time})
        widget_max_date_time = qdatetime_to_python(
            self.datetime_edit.widget.maximumDateTime())
        self.assertEqual(widget_max_date_time, max_date_time)

    def test_set_datetime_format(self):
        """ Test the QtDatetimeEdit's set_datetime_format command

        """
        date_time_format = 'd M y - hh:mm:ss'
        self.datetime_edit.recv('set_datetime_format', {'value':date_time_format})
        widget_format = self.datetime_edit.widget.displayFormat()
        self.assertEqual(widget_format, date_time_format)

if __name__ == '__main__':
    app = QApplication([])
    unittest.main()
