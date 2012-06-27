#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_menu import QtMenu
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtMenuBar(object):
    """ Unit tests for the QtMenuBar

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
    
    def setUp(self):
        """ Set up the widget for testing

        """
        self.menu = QtMenu(None, uuid4().hex, QtLocalPipe(), QtLocalPipe())
        self.menu.create()

    def test_set_title(self):
        """ Test the QtMenu's set_title command

        """
        title = 'Menu title'
        self.menu.recv('set_title', {'value':title})
        assert self.menu.widget.title() == title
