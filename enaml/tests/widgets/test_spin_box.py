#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.validation.api import IntValidator

from .enaml_test_case import EnamlTestCase


class TestSpinBox(EnamlTestCase):
    """ Unit tests for the SpinBox widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import SpinBox, Window

enamldef MainView(Window):
    SpinBox:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "SpinBox")
        self.client_widget = self.find_client_widget(self.client_view, "QtSpinBox")

    def test_set_maximum(self):
        """ Test the setting of a SpinBox's maximum attribute
        """
        with self.app.process_events():
            self.server_widget.maximum = 1000

        self.assertEquals(self.client_widget.maximum(), self.server_widget.maximum)

    def test_set_minimum(self):
        """ Test the setting of a SpinBox's minimum attribute
        """
        with self.app.process_events():
            self.server_widget.minimum = 10

        self.assertEquals(self.client_widget.minimum(), self.server_widget.minimum)

    def test_set_single_step(self):
        """ Test the setting of a SpinBox's single_step attribute
        """
        with self.app.process_events():
            self.server_widget.single_step = 25

        self.assertEquals(self.client_widget.singleStep(), self.server_widget.single_step)

    def test_set_value(self):
        """ Test the setting of a SpinBox's value attribute
        """
        with self.app.process_events():
            self.server_widget.value = 50

        self.assertEquals(self.client_widget.value(), self.server_widget.value)

    def test_set_wrap(self):
        """ Test the setting of a SpinBox's wrap attribute
        """
        with self.app.process_events():
            self.server_widget.wrapping = True

        self.assertEquals(self.client_widget.wrapping(), self.server_widget.wrapping)

    ### Need to add tests for special_value_text, prefix, suffix and read_only

if __name__ == '__main__':
    import unittest
    unittest.main()
