#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication, QTabWidget, QWidget
from enaml.qt.qt_tab_group import QtTabGroup
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtTabGroup(object):
    """ Unit tests for the QtTabGroup

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
    
    def setUp(self):
        """ Set up the widget for testing

        """
        self.tab_group = QtTabGroup(None, uuid4().hex, QtLocalPipe(),
                                    QtLocalPipe())
        self.tab_group.create()

    def test_set_selected_index(self):
        """ Test QtTabGroup's set_selected_index command

        """
        for i in range(3):
            self.tab_group.widget.addTab(QWidget(self.tab_group.widget), 'tab%s' % (i+1))

        ind = 1
        self.tab_group.recv('set_selected_index', {'value':ind})
        assert self.tab_group.widget.currentIndex() == ind

    def test_set_tab_position(self):
        """ Test the QtTabGroup's set_tab_position command

        """
        self.tab_group.recv('set_tab_position', {'value':'right'})
        assert self.tab_group.widget.tabPosition() == QTabWidget.East        
