#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtCore import Qt
from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_dialog import QtDialog
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtDialog(object):
    """ Unit tests for the QtDialog
    
    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
        
    def setUp(self):
        """ Set up the widget for testing

        """
        self.dialog = QtDialog(None, uuid4().hex, QtLocalPipe(uuid4))
        self.dialog.create()

    def test_set_modality(self):
        """ Test the set_modality command of the QtDialog

        """
        self.dialog.recv_message({'action':'set-modality',
				  'modality':'application_modal'})
        assert self.dialog.widget.windowModality() == Qt.ApplicationModal
