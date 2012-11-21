#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestToggleControl(EnamlTestCase):
    """ Unit tests for the ToggleControl widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Window
from enaml.widgets.push_button import PushButton

enamldef MainView(Window):
    PushButton:
        checkable = True
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "PushButton")
        self.client_widget = self.find_client_widget(self.client_view, "PushButton")

    def test_set_checked(self):
        """ Test the setting of a ToggleControl's checked attribute
        """
        self.server_widget.checked = True
        assert self.client_widget.checked == self.server_widget.checked

    def test_set_text(self):
        """ Test the setting of a ToggleControl's text attribute
        """
        self.server_widget.text = "Toggle Me!"
        assert self.client_widget.text == self.server_widget.text

