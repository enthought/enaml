#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_push_button import QtPushButton
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtPushButton(object):
    """ Unit tests for the QtPushButton

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
    
    def setUp(self):
        """ Set up the widget for testing

        """
        self.button = QtPushButton(None, uuid4().hex, QtLocalPipe(uuid4))
        self.button.create()

    def test_set_text(self):
        """ Test the QtPushButton's set_text command

        """
        text = "Button"
        self.button.recv_message({'action':'set-text', 'text':text})
        assert self.button.widget.text() == text
