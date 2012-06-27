#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_label import QtLabel
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtLabel(object):
    """ Unit tests for the QtLabel

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
            
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
        assert self.label.widget.text() == text

    def test_set_word_wrap(self):
        """ Test the QtLabel's set_word_wrap command

        """
        wrap = True
        self.label.recv('set_word_wrap', {'value':wrap})
        assert self.label.widget.wordWrap() == wrap
