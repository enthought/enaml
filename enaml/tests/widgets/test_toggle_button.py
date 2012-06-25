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
from enaml.widgets import ToggleButton, Window

enamldef MainView(Window):
    ToggleButton:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "ToggleButton")
        self.client_widget = self.find_client_widget(self.client_view, "ToggleButton")

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

