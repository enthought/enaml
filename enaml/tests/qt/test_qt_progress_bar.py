#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_progress_bar import QtProgressBar
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtProgressBar(unittest.TestCase):
    """ Unit tests for the QtProgressBar

    """
    def setUp(self):
        """ Set up the widget for testing

        """
        self.progress_bar = QtProgressBar(None, uuid4().hex, QtLocalPipe(),
                                          QtLocalPipe())
        self.progress_bar.create()

    def test_set_maximum(self):
        """ Test the QtProgressBar's set_maximum command

        """
        maximum = 20
        self.progress_bar.recv('set_maximum', {'value':maximum})
        self.assertEqual(self.progress_bar.widget.maximum(), maximum)

    def test_set_minimum(self):
        """ Test the QtProgressBar's set_minimum command

        """
        minimum = 10
        self.progress_bar.recv('set_minimum', {'value':minimum})
        self.assertEqual(self.progress_bar.widget.minimum(), minimum)

    def test_set_value(self):
        """ Test the QtProgressBar's set_value command

        """
        value = 15
        self.progress_bar.recv('set_value', {'value':value})
        self.assertEqual(self.progress_bar.widget.value(), value)

if __name__ == '__main__':
    app = QApplication([])
    unittest.main()
