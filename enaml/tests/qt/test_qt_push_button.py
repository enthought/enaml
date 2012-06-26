#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_push_button import QtPushButton
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtPushButton(unittest.TestCase):
    """ Unit tests for the QtPushButton

    """
    def setUp(self):
        """ Set up the widget for testing

        """
        self.button = QtPushButton(None, uuid4().hex, QtLocalPipe(),
                                 QtLocalPipe())
        self.button.create()

    def test_set_text(self):
        """ Test the QtPushButton's set_text command

        """
        text = "Button"
        self.button.recv('set_text', {'value':text})
        self.assertEqual(self.button.widget.text(), text)

if __name__ == '__main__':
    app = QApplication([])
    unittest.main()
