#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestToggleButton(EnamlTestCase):
    """ Unit tests for the ToggleButton widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import PushButton, Window

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


    def test_set_icon(self):
        """ Test the setting of a ToggleButton's icon attribute
        """
        # XXX: figure this out
        pass

    def test_set_icon_size(self):
        """ Test the setting of a ToggleButton's icon_size attribute
        """
        # XXX: figure this out
        pass

