#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_label import QtLabel
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtLabel(unittest.TestCase):
    """ Unit tests for the QtLabel

    """
    def setUp(self):
        """ Set up the widget for testing

        """
        self.label = QtLabel(None, uuid4().hex, QtLocalPipe(),
                             QtLocalPipe())
        self.label.create()

    def test_set_text(self):
        """ Test the QtLabel's set_text command

        """
        text = "test"
        self.label.recv('set_text', {'value':text})
        self.assertEqual(self.label.widget.text(), text)

    def test_set_word_wrap(self):
        """ Test the QtLabel's set_word_wrap command

        """
        wrap = True
        self.label.recv('set_word_wrap', {'value':wrap})
        self.assertEqual(self.label.widget.wordWrap(), wrap)

if __name__ == '__main__':
    app = QApplication([])
    unittest.main()
