#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_combo_box import QtComboBox
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtComboBox(object):
    """ Unit tests for the QtComboBox

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
    
    def setUp(self):
        """ Set up the widget for testing

        """
        self.combo_box = QtComboBox(None, uuid4().hex, QtLocalPipe(),
                                    QtLocalPipe())
        self.combo_box.create()

    def test_set_items(self):
        """ Test the QtComboBox's set_items command

        """
        items = ['one', 'two', 'three']
        self.combo_box.recv('set_items', {'value':items})
        widget_items = []
        for ind in range(self.combo_box.widget.count()):
            widget_items.append(self.combo_box.widget.itemText(ind))
        assert widget_items == items

    def test_set_index(self):
        """ Test the QtComboBox's set_index command

        """
        # We have to add items to the combo box so that there is a 0th index,
        # otherwise the index will stay -1 when we try to set it to 0
        self.combo_box.widget.addItems(['one', 'two', 'three'])
        
        index = 0
        self.combo_box.recv('set_index', {'value':index})
        widget_index = self.combo_box.widget.currentIndex()
        assert widget_index == index
