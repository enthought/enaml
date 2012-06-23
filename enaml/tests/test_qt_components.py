#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest, os, datetime
from enaml.qt.qt import QtCore
from enaml.qt.qt.QtGui import QApplication, QFileDialog
from enaml.qt.qt_local_pipe import QtLocalPipe

# Workarounds for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPython
except AttributeError: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPyDate

try: # pragma: no cover
    qdatetime_to_python = QtCore.QDateTime.toPython
except AttributeError: # pragma: no cover
    qdatetime_to_python = QtCore.QDateTime.toPyDateTime

from enaml.qt.qt_calendar import QtCalendar
from enaml.qt.qt_date_edit import QtDateEdit
from enaml.qt.qt_datetime_edit import QtDatetimeEdit
from enaml.qt.qt_combo_box import QtComboBox
from enaml.qt.qt_window import QtWindow
from enaml.qt.qt_dialog import QtDialog
from enaml.qt.qt_directory_dialog import QtDirectoryDialog
from enaml.qt.qt_file_dialog import QtFileDialog

class TestQtComponents(unittest.TestCase):
    """ Unit tests for the Qt components

    """
    def test_calendar(self):
        """ Test the QtCalendar

        """
        calendar = QtCalendar(None, QtLocalPipe(), QtLocalPipe())
        calendar.create()

        date = datetime.date.today()
        calendar.recv('set_date', {'value':date})
        widget_date = qdate_to_python(calendar.widget.selectedDate())
        self.assertEqual(widget_date, date)

        max_date = datetime.date(7999, 12, 31)
        calendar.recv('set_max_date', {'value':max_date})
        widget_max_date = qdate_to_python(calendar.widget.maximumDate())
        self.assertEqual(widget_max_date, max_date)
        
        min_date = datetime.date(1752, 9, 14)
        calendar.recv('set_min_date', {'value':min_date})
        widget_min_date = qdate_to_python(calendar.widget.minimumDate())
        self.assertEqual(widget_min_date, min_date)

    def test_date_edit(self):
        """ Test the QtDateEdit

        """
        date_edit = QtDateEdit(None, QtLocalPipe(), QtLocalPipe())
        date_edit.create()

        display_format = 'MMMM dd, YYYY'
        date_edit.recv('set_date_format', {'value':display_format})
        widget_format = date_edit.widget.displayFormat()
        self.assertEqual(widget_format, display_format)

        date = datetime.date.today()
        date_edit.recv('set_date', {'value':date})
        widget_date = qdate_to_python(date_edit.widget.date())
        self.assertEqual(widget_date, date)

        max_date = datetime.date(7999, 12, 31)
        date_edit.recv('set_max_date', {'value':max_date})
        widget_max_date = qdate_to_python(date_edit.widget.maximumDate())
        self.assertEqual(widget_max_date, max_date)
        
        min_date = datetime.date(1752, 9, 14)
        date_edit.recv('set_min_date', {'value':min_date})
        widget_min_date = qdate_to_python(date_edit.widget.minimumDate())
        self.assertEqual(widget_min_date, min_date)

    def test_datetime_edit(self):
        """ Test the QtDatetimeEdit

        """
        datetime_edit = QtDatetimeEdit(None, QtLocalPipe(), QtLocalPipe())
        datetime_edit.create()

        date_time = datetime.datetime(2012,6,22,0,0,0,0)
        datetime_edit.recv('set_datetime', {'value':date_time})
        widget_date_time = qdatetime_to_python(datetime_edit.widget.dateTime())
        self.assertEqual(widget_date_time, date_time)

        min_date_time = datetime.datetime(1752,9,14, 0, 0, 0, 0)
        datetime_edit.recv('set_min_datetime', {'value':min_date_time})
        widget_min_date_time = qdatetime_to_python(
            datetime_edit.widget.minimumDateTime())
        self.assertEqual(widget_min_date_time, min_date_time)

        max_date_time = datetime.datetime(7999, 12, 31, 23, 59, 59, 999000)
        datetime_edit.recv('set_max_datetime', {'value':max_date_time})
        widget_max_date_time = qdatetime_to_python(
            datetime_edit.widget.maximumDateTime())
        self.assertEqual(widget_max_date_time, max_date_time)

        date_time_format = 'd M y - hh:mm:ss'
        datetime_edit.recv('set_datetime_format', {'value':date_time_format})
        widget_format = datetime_edit.widget.displayFormat()
        self.assertEqual(widget_format, date_time_format)

    def test_combo_box(self):
        """ Test the QtComboBox

        """
        combo_box = QtComboBox(None, QtLocalPipe(), QtLocalPipe())
        combo_box.create()

        items = ['one', 'two', 'three']
        combo_box.recv('set_items', {'value':items})
        widget_items = []
        for ind in range(combo_box.widget.count()):
            widget_items.append(combo_box.widget.itemText(ind))
        self.assertEqual(widget_items, items)

        index = 0
        combo_box.recv('set_index', {'value':index})
        widget_index = combo_box.widget.currentIndex()
        self.assertEqual(widget_index, index)
        
    def test_window(self):
        """ Test the QtWindow

        """
        window = QtWindow(None, QtLocalPipe(), QtLocalPipe())
        window.create()

        title_str = 'Test title'
        window.recv('set_title', {'value':title_str})
        self.assertEqual(window.widget.windowTitle(), title_str)

        initial_size = (200,200)
        window.recv('set_initial_size', {'value':initial_size})
        q_size = window.widget.size()
        widget_size = (q_size.width(), q_size.height())
        self.assertEqual(widget_size, initial_size)

        maximum_size = (1000,1000)
        window.recv('set_maximum_size', {'value':maximum_size})
        q_max_size = window.widget.maximumSize()
        widget_max_size = (q_max_size.width(), q_max_size.height())
        self.assertEqual(widget_max_size, maximum_size)

        minimum_size = (10, 10)
        window.recv('set_minimum_size', {'value':minimum_size})
        q_min_size = window.widget.minimumSize()
        widget_min_size = (q_min_size.width(), q_min_size.height())
        self.assertEqual(widget_min_size, minimum_size)

        window.recv('minimize', {})
        self.assertEqual(window.widget.isMinimized(), True)

        window.recv('maximize', {})
        self.assertEqual(window.widget.isMaximized(), True)

        window.recv('restore', {})
        self.assertEqual(window.widget.isMaximized(), False)

        #XXX if size hints are implemented this is not a sure way to test for
        # defaults
        initial_size_default = (50, 50)
        window.recv('set_initial_size_default', {'value':initial_size_default})
        window.recv('set_initial_size', {'value':(-1,-1)})
        init_d_size = (window.widget.size().width(),
                       window.widget.size().height())
        self.assertEqual(init_d_size, initial_size_default)

        maximum_size_default = (500, 500)
        window.recv('set_maximum_size_default', {'value':maximum_size_default})
        window.recv('set_maximum_size', {'value':(-1,-1)})
        max_d_size = (window.widget.maximumSize().width(),
                      window.widget.maximumSize().height())
        self.assertEqual(max_d_size, maximum_size_default)

        minimum_size_default = (5, 5)
        window.recv('set_minimum_size_default', {'value':minimum_size_default})
        window.recv('set_minimum_size', {'value':(-1,-1)})
        min_d_size = (window.widget.minimumSize().width(),
                      window.widget.minimumSize().height())
        self.assertEqual(min_d_size, minimum_size_default)

        window.recv('show', {})
        self.assertEqual(window.widget.isVisible(), True)

    def test_dialog(self):
        """ Test the QtDialog

        """
        dialog = QtDialog(None, QtLocalPipe(), QtLocalPipe())
        dialog.create()

        dialog.recv('set_modality', {'value':'application_modal'})
        self.assertEqual(dialog.widget.windowModality(),
                         QtCore.Qt.ApplicationModal)

        #XXX Dialog events need to be reimplemented

    def test_directory_dialog(self):
        """ Test the QtDirectoryDialog. Note that this test will fail if the
        tested directory does not exist in the file system

        """
        dir_dialog = QtDirectoryDialog(None, QtLocalPipe(), QtLocalPipe())
        dir_dialog.create()

        # The test will fail if this directory does not exist, so we use
        # the current directory to ensure that it exists
        dir_path = os.path.abspath(os.path.curdir)
        dir_dialog.recv('set_directory', {'value':dir_path})
        widget_path = dir_dialog.widget.directory().absolutePath()
        self.assertEqual(widget_path, dir_path)

    def test_file_dialog(self):
        """ Test the QtFileDialog

        """
        file_dialog = QtFileDialog(None, QtLocalPipe(), QtLocalPipe())
        file_dialog.create()

        file_dialog.recv('set_mode', {'value':'open'})
        mode = file_dialog.widget.acceptMode()
        self.assertEqual(mode, QFileDialog.AcceptOpen)

        file_dialog.recv('set_multi_select', {'value':True})
        multi = file_dialog.widget.fileMode()
        self.assertEqual(multi, QFileDialog.ExistingFiles)

        dir_path = os.path.abspath(os.path.curdir)
        file_dialog.recv('set_directory', {'value':dir_path})
        widget_path = file_dialog.widget.directory().absolutePath()
        self.assertEqual(widget_path, dir_path)

        file_path = os.path.abspath(__file__)
        file_dialog.recv('set_filename', {'value':file_path})
        widget_file_path = file_dialog.widget.selectedFiles()[0]
        self.assertEqual(widget_file_path, file_path)

        filters = ['Python files (.py)']
        file_dialog.recv('set_filters', {'value':filters})
        widget_filters = file_dialog.widget.nameFilters()
        self.assertEqual(widget_filters, filters)

    def test_main_window(self):
        """ Test QtMainWindow

        """
        # XXX Events in unit tests? We can force the signal to emit,
        # but I can't think of a way to assert or test anything here
        pass
        
        

if __name__ == '__main__':
    app = QApplication([])
    unittest.main()
