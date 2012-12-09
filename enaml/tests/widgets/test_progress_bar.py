#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestProgressBar(EnamlTestCase):
    """ Unit tests for the ProgressBar widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import ProgressBar, Window

enamldef MainView(Window):
    ProgressBar:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "ProgressBar")
        self.client_widget = self.find_client_widget(self.client_view, "QtProgressBar")

    def test_set_maximum(self):
        """ Test the setting of a ProgressBar's maximum attribute
        """
        with self.app.process_events():
            self.server_widget.maximum = 1000

        self.assertEquals(self.client_widget.maximum(), self.server_widget.maximum)

    def test_set_minimum(self):
        """ Test the setting of a ProgressBar's minimum attribute
        """
        with self.app.process_events():
            self.server_widget.minimum = 10

        self.assertEquals(self.client_widget.minimum(), self.server_widget.minimum)

    def test_set_value(self):
        """ Test the setting of a ProgressBar's value attribute
        """
        with self.app.process_events():
            self.server_widget.value = 50

        self.assertEquals(self.client_widget.value(), self.server_widget.value)

