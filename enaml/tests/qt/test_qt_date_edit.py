#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest, datetime
from uuid import uuid4

from enaml.qt.qt import QtCore
from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_date_edit import QtDateEdit
from enaml.qt.qt_local_pipe import QtLocalPipe

# Workarounds for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPython
except AttributeError: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPyDate

class TestQtDateEdit(unittest.TestCase):
    """ Unit tests for the QtDateEdit

    """
    def setUp(self):
        """ Set up the widget for testing

        """
        self.date_edit = QtDateEdit(None, uuid4().hex, QtLocalPipe(),
                                    QtLocalPipe())
        self.date_edit.create()

    def test_set_date_format(self):
        """ Test the QtDateEdit's set_date_format command

        """
        display_format = 'MMMM dd, YYYY'
        self.date_edit.recv('set_date_format', {'value':display_format})
        widget_format = self.date_edit.widget.displayFormat()
        self.assertEqual(widget_format, display_format)

    def test_set_date(self):
        """ Test the QtDateEdit's set_date command

        """
        date = datetime.date.today()
        self.date_edit.recv('set_date', {'value':date})
        widget_date = qdate_to_python(self.date_edit.widget.date())
        self.assertEqual(widget_date, date)

    def test_set_max_date(self):
        """ Test the QtDateEdit's set_max_date command

        """
        max_date = datetime.date(7999, 12, 31)
        self.date_edit.recv('set_max_date', {'value':max_date})
        widget_max_date = qdate_to_python(self.date_edit.widget.maximumDate())
        self.assertEqual(widget_max_date, max_date)

        
    def test_set_min_date(self):
        """ Test the QtDateEdit's set_min_date command

        """
        min_date = datetime.date(1752, 9, 14)
        self.date_edit.recv('set_min_date', {'value':min_date})
        widget_min_date = qdate_to_python(self.date_edit.widget.minimumDate())
        self.assertEqual(widget_min_date, min_date)
 
if __name__ == '__main__':
    app = QApplication([])
    unittest.main()
