#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_window import QtWindow
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtWindow(unittest.TestCase):
    """ Unit tests for the QtWindow

    """
    def setUp(self):
        """ Set up the widget for testing

        """
        self.window = QtWindow(None, uuid4().hex, QtLocalPipe(),
                               QtLocalPipe())
        self.window.create()

    def test_set_title(self):
        """ Test the set_title command of the QtWindow

        """
        title_str = 'Test title'
        self.window.recv('set_title', {'value':title_str})
        self.assertEqual(self.window.widget.windowTitle(), title_str)

    def test_set_max_size(self):
        """ Test the QtWindow's set_max_size command

        """
        maximum_size = (1000,1000)
        self.window.recv('set_max_size', {'value':maximum_size})
        q_max_size = self.window.widget.maximumSize()
        widget_max_size = (q_max_size.width(), q_max_size.height())
        self.assertEqual(widget_max_size, maximum_size)

    def test_set_min_size(self):
        """ Test the QtWindow's set_min_size command

        """
        minimum_size = (10, 10)
        self.window.recv('set_min_size', {'value':minimum_size})
        q_min_size = self.window.widget.minimumSize()
        widget_min_size = (q_min_size.width(), q_min_size.height())
        self.assertEqual(widget_min_size, minimum_size)

    def test_minimize(self):
        """ Test the QtWindow's minimize command

        """
        self.window.recv('minimize', {})
        self.assertEqual(self.window.widget.isMinimized(), True)

    def test_maximize(self):
        """ Test the QtWindow's maximize command

        """
        self.window.recv('maximize', {})
        self.assertEqual(self.window.widget.isMaximized(), True)

    def test_restore(self):
        """ Test the QtWindow's restore command

        """
        self.window.recv('restore', {})
        self.assertEqual(self.window.widget.isMaximized(), False)

if __name__ == '__main__':
    app = QApplication([])
    unittest.main()
