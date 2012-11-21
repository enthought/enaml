#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestFloatSlider(EnamlTestCase):
    """ Unit tests for the FloatSlider widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import FloatSlider, Window

enamldef MainView(Window):
    FloatSlider:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "FloatSlider")
        self.client_widget = self.find_client_widget(self.client_view, "FloatSlider")

    def test_set_precision(self):
        """ Test the setting of a FloatSlider's precision attribute
        """
        self.server_widget.precision = 10000
        assert self.client_widget.precision == self.server_widget.precision

