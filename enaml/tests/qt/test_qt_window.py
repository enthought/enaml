#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_window import QtWindow
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtWindow(object):
    """ Unit tests for the QtWindow

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
            
    def setUp(self):
        """ Set up the widget for testing

        """
        self.window = QtWindow(None, uuid4().hex, QtLocalPipe(uuid4))
        self.window.create()

    def test_set_title(self):
        """ Test the set_title command of the QtWindow

        """
        title_str = 'Test title'
        self.window.recv_message({'action':'set-title',
                                  'title':title_str})
        assert self.window.widget.windowTitle() == title_str

    def test_minimize(self):
        """ Test the QtWindow's minimize command

        """
        self.window.recv_message({'action':'minimize'})
        assert self.window.widget.isMinimized() == True

    def test_maximize(self):
        """ Test the QtWindow's maximize command

        """
        self.window.recv_message({'action':'maximize'})
        assert self.window.widget.isMaximized() == True

    def test_restore(self):
        """ Test the QtWindow's restore command

        """
        self.window.recv_message({'action':'restore'})
        assert self.window.widget.isMaximized() == False
