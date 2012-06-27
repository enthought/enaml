#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime
from uuid import uuid4

from enaml.qt.qt import QtCore
from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_calendar import QtCalendar
from enaml.qt.qt_local_pipe import QtLocalPipe

# Workarounds for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPython
except AttributeError: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPyDate

class TestQtCalendar(object):
    """ Unit tests for the QtCalendar

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
        
    def setUp(self):
        """ Set up the widget for testing

        """
        self.calendar = QtCalendar(None, uuid4().hex, QtLocalPipe(),
                                   QtLocalPipe())
        self.calendar.create()
        
    def test_set_date(self):
        """ Test the QtCalendar's set_date command

        """
        date = datetime.date.today()
        self.calendar.recv('set_date', {'value':date})
        widget_date = qdate_to_python(self.calendar.widget.selectedDate())
        assert widget_date == date

    def test_set_max_date(self):
        """ Test the QtCalendar's set_max_date command

        """
        max_date = datetime.date(7999, 12, 31)
        self.calendar.recv('set_max_date', {'value':max_date})
        widget_max_date = qdate_to_python(self.calendar.widget.maximumDate())
        assert widget_max_date == max_date
        
    def test_set_min_date(self):
        """ Test the QtCalendar's set_min_date command

        """
        min_date = datetime.date(1752, 9, 14)
        self.calendar.recv('set_min_date', {'value':min_date})
        widget_min_date = qdate_to_python(self.calendar.widget.minimumDate())
        assert widget_min_date == min_date
