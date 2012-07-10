#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtCore import Qt
from enaml.qt.qt.QtGui import QApplication, QSlider
from enaml.qt.qt_slider import QtSlider
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtSlider(object):
    """ Unit tests for the QtSlider

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
            
    def setUp(self):
        """ Set up the widget for testing

        """
        self.slider = QtSlider(None, uuid4().hex, QtLocalPipe(uuid4))
        self.slider.create()

    def test_set_maximum(self):
        """ Test the QtSlider's set_maximum command

        """
        maximum = 50
	self.slider.recv_message({'action':'set-maximum',
				  'maximum':maximum})
        assert self.slider.widget.maximum() == maximum

    def test_set_minimum(self):
        """ Test the QtSlider's set_minimum command

        """
        minimum = 10
	self.slider.recv_message({'action':'set-minimum',
				  'minimum':minimum})
        assert self.slider.widget.minimum() == minimum

    def test_set_value(self):
        """ Test the QtSlider's set_value command

        """
        value = 20
	self.slider.recv_message({'action':'set-value',
				  'value':value})
        assert self.slider.widget.value() == value

    def test_set_orientation(self):
        """ Test the QtSlider's set_orientation command

        """
        self.slider.recv_message({'action':'set-orientation',
				  'orientation':'vertical'})
        assert self.slider.widget.orientation() == Qt.Vertical

    def test_set_page_step(self):
        """ Test the QtSlider's set_page_step command

        """
        step = 2
	self.slider.recv_message({'action':'set-page_step',
				  'page_step':step})
        assert self.slider.widget.pageStep() == step

    def test_set_single_step(self):
        """ Test the QtSlider's set_single_step command

        """
        step = 10
	self.slider.recv_message({'action':'set-single_step',
				  'single_step':step})
        assert self.slider.widget.singleStep() == step

    def test_set_tick_interval(self):
        """ Test the QtSlider's set_tick_interval command

        """
        interval = 5
	self.slider.recv_message({'action':'set-tick_interval',
				  'tick_interval':interval})
        assert self.slider.widget.tickInterval() == interval

    def test_set_tick_position(self):
        """ Test the QtSlider's set_tick_position command

        """
        self.slider.recv_message({'action':'set-tick_position',
				  'tick_position':'left'})
        assert self.slider.widget.tickPosition() == QSlider.TicksLeft

    def test_set_tracking(self):
        """ Test the QtSlider's set_tracking command

        """
        self.slider.recv_message({'action':'set-tracking',
				  'tracking':False})
        assert self.slider.widget.hasTracking() == False
