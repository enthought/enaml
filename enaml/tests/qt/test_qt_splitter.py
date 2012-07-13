#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtCore import Qt
from enaml.qt.qt.QtGui import QApplication, QWidget
from enaml.qt.qt_splitter import QtSplitter
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtSplitter(object):
    """ Unit tests for the QtSplitter
    
    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
        
    def setUp(self):
        """ Set up the widget for testing

        """
        self.splitter = QtSplitter(None, uuid4().hex, QtLocalPipe(uuid4))
        self.splitter.create()

    def test_set_orientation(self):
        """ Test the QtSplitter's set_orientation command

        """
        self.splitter.recv_message({'action':'set-orientation',
				    'orientation':'vertical'})
        assert self.splitter.widget.orientation() == Qt.Vertical

    def test_set_live_drag(self):
        """ Test the QtSplitter's set_live_drag command

        """
        self.splitter.recv_message({'action':'set-live_drag',
				    'live_drag':False})
        assert self.splitter.widget.opaqueResize() == False

    def test_set_preferred_sizes(self):
        """ Test the QtSplitter's set_preferred_sizes command

        """
        for i in range(2):
            self.splitter.widget.addWidget(QWidget(self.splitter.widget))

        old_sizes = self.splitter.widget.sizes()
        sizes = [350, 350]
	self.splitter.recv_message({'action':'set-preferred_sizes',
				    'preferred_sizes':sizes})
        # Qt manipulates the sizes somewhat to conform to the layout,
        # so the best we can do is check that the sizes have changed
        assert self.splitter.widget.sizes() != old_sizes
