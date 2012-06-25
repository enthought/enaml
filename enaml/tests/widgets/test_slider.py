#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestSlider(EnamlTestCase):
    """ Unit tests for the Slider widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets import Slider, Window

enamldef MainView(Window):
    Slider:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "Slider")
        self.client_widget = self.find_client_widget(self.client_view, "Slider")

    def test_set_maximum(self):
        """ Test the setting of a Slider's maximum attribute
        """
        self.server_widget.maximum = 1000
        assert self.client_widget.maximum == self.server_widget.maximum

    def test_set_minimum(self):
        """ Test the setting of a Slider's minimum attribute
        """
        self.server_widget.minimum = 10
        assert self.client_widget.minimum == self.server_widget.minimum

    def test_set_orientation(self):
        """ Test the setting of a Slider's orientation attribute
        """
        self.server_widget.orientation = 'vertical'
        assert self.client_widget.orientation == self.server_widget.orientation

    def test_set_page_step(self):
        """ Test the setting of a Slider's page_step attribute
        """
        self.server_widget.page_step = 25
        assert self.client_widget.page_step == self.server_widget.page_step

    def test_set_single_step(self):
        """ Test the setting of a Slider's single_step attribute
        """
        self.server_widget.single_step = 50
        assert self.client_widget.single_step == self.server_widget.single_step

    def test_set_tick_interval(self):
        """ Test the setting of a Slider's tick_interval attribute
        """
        self.server_widget.tick_interval = 13
        assert self.client_widget.tick_interval == self.server_widget.tick_interval

    def test_set_tick_position(self):
        """ Test the setting of a Slider's tick_position attribute
        """
        self.server_widget.tick_position = 'top'
        assert self.client_widget.tick_position == self.server_widget.tick_position

    def test_set_tracking(self):
        """ Test the setting of a Slider's tracking attribute
        """
        self.server_widget.tracking = False
        assert self.client_widget.tracking == self.server_widget.tracking

    def test_set_value(self):
        """ Test the setting of a Slider's value attribute
        """
        self.server_widget.value = 75
        assert self.client_widget.value == self.server_widget.value

