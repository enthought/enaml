#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from uuid import uuid4

from enaml.qt.qt.QtCore import Qt
from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_dialog import QtDialog
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtDialog(unittest.TestCase):
    """ Unit tests for the QtDialog
    
    """
    def setUp(self):
        """ Set up the widget for testing

        """
        self.dialog = QtDialog(None, uuid4().hex, QtLocalPipe(),
                               QtLocalPipe())
        self.dialog.create()

    def test_set_modality(self):
        """ Test the set_modality command of the QtDialog

        """
        self.dialog.recv('set_modality', {'value':'application_modal'})
        self.assertEqual(self.dialog.widget.windowModality(),
                         Qt.ApplicationModal)

if __name__ == '__main__':
    app = QApplication([])
    unittest.main()
