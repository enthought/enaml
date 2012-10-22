#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestPushButton(EnamlTestCase):
    """ Unit tests for the PushButton widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import PushButton, Window

enamldef MainView(Window):
    PushButton:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "PushButton")
        self.client_widget = self.find_client_widget(self.client_view, "PushButton")

    def test_(self):
        """ Test the setting of a PushButton's text attribute
        """
        self.server_widget.text = "Push Me!"
        assert self.client_widget.text == self.server_widget.text

