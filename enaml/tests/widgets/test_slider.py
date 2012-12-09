#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase

from enaml.qt.qt_slider import _ORIENTATION_MAP, _TICK_POSITION_MAP


class TestSlider(EnamlTestCase):
    """ Unit tests for the Slider widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Slider, Window

enamldef MainView(Window):
    Slider:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "Slider")
        self.client_widget = self.find_client_widget(self.client_view, "QtSlider")

    def test_set_maximum(self):
        """ Test the setting of a Slider's maximum attribute
        """
        with self.app.process_events():
            self.server_widget.maximum = 1000

        self.assertEquals(self.client_widget.maximum(), self.server_widget.maximum)

    def test_set_minimum(self):
        """ Test the setting of a Slider's minimum attribute
        """
        with self.app.process_events():
            self.server_widget.minimum = 10

        self.assertEquals(self.client_widget.minimum(), self.server_widget.minimum)

    def test_set_orientation(self):
        """ Test the setting of a Slider's orientation attribute
        """
        with self.app.process_events():
            self.server_widget.orientation = 'vertical'

        self.assertEquals(
            self.client_widget.orientation(),
             _ORIENTATION_MAP[self.server_widget.orientation]
        )

    def test_set_page_step(self):
        """ Test the setting of a Slider's page_step attribute
        """
        with self.app.process_events():
            self.server_widget.page_step = 25

        self.assertEquals(self.client_widget.pageStep(), self.server_widget.page_step)

    def test_set_single_step(self):
        """ Test the setting of a Slider's single_step attribute
        """
        with self.app.process_events():
            self.server_widget.single_step = 50

        self.assertEquals(self.client_widget.singleStep(), self.server_widget.single_step)

    def test_set_tick_interval(self):
        """ Test the setting of a Slider's tick_interval attribute
        """
        with self.app.process_events():
            self.server_widget.tick_interval = 13

        assert self.client_widget.tickInterval() == self.server_widget.tick_interval

    def test_set_tick_position(self):
        """ Test the setting of a Slider's tick_position attribute
        """
        with self.app.process_events():
            self.server_widget.tick_position = 'top'

        self.assertEquals(
            self.client_widget.tickPosition(),
            _TICK_POSITION_MAP[self.server_widget.tick_position]
        )

    def test_set_tracking(self):
        """ Test the setting of a Slider's tracking attribute
        """
        with self.app.process_events():
            self.server_widget.tracking = False

        self.assertEquals(self.client_widget.hasTracking(), self.server_widget.tracking)

    def test_set_value(self):
        """ Test the setting of a Slider's value attribute
        """
        with self.app.process_events():
            self.server_widget.value = 75

        self.assertEquals(self.client_widget.value(), self.server_widget.value)

if __name__ == '__main__':
    import unittest
    unittest.main()

