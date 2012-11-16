#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtCore import Qt
from enaml.qt.qt.QtGui import QApplication, QWidget
from enaml.qt.qt_scroll_area import QtScrollArea
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtScrollArea(object):
    """ Unit tests for the QtScrollArea

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
    
    def setUp(self):
        """ Set up the widget for testing

        """
        self.scroll_area = QtScrollArea(None, uuid4().hex, QtLocalPipe(uuid4))
        self.scroll_area.create()

    def test_set_horizontal_scroll_policy(self):
        """ Test the QtScrollArea's set_horizontal_scroll_policy command

        """
        self.scroll_area.recv_message({'action':'set-horizontal_scroll_policy',
				       'horizontal_scroll_policy':'always_off'})
        widget_policy =  self.scroll_area.widget.horizontalScrollBarPolicy()
        assert widget_policy == Qt.ScrollBarAlwaysOff

    def test_set_preferred_size(self):
        """ Test the QtScrollArea's set_preferred_size command

        """
        # XXX size hint?
        pass

    def test_set_scroll_position(self):
        """ Test the QtScrollArea's set_scroll_position command

        """
        pos = (10, 20)
        
        # we have to set the maximum values so that when we
        # set the values they fall within the correct range
        self.scroll_area.widget.horizontalScrollBar().setMaximum(50)
        self.scroll_area.widget.verticalScrollBar().setMaximum(50)
        
	self.scroll_area.recv_message({'action':'set-scroll_position',
				       'scroll_position':pos})
        widget = self.scroll_area.widget
        widget_h_pos = widget.horizontalScrollBar().value()
        widget_v_pos = widget.verticalScrollBar().value()

        assert (widget_h_pos, widget_v_pos) == pos

    def test_set_scrolled_component(self):
        """ Test the QtScrollArea's set_scrolled_component command

        """
        comp = QWidget()
	self.scroll_area.recv_message({'action':'set-scrolled_component',
				       'scrolled_component':comp})
        assert self.scroll_area.widget.viewport() == comp

    def test_set_vertical_scroll_policy(self):
        """ Test the QtScrollArea's set_vertical_scroll_policy command

        """
        self.scroll_area.recv_message({'action':'set-vertical_scroll_policy',
				       'vertical_scroll_policy':'always_off'})
        widget_policy =  self.scroll_area.widget.verticalScrollBarPolicy()
        assert widget_policy == Qt.ScrollBarAlwaysOff
        
