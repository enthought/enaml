#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestWindow(EnamlTestCase):
    """ Unit tests for the Window widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets import Window

enamldef MainView(Window):
    title = ""
"""
        self.parse_and_create(enaml_source)
        self.server_window = self.find_server_widget(self.view, "Window")
        self.client_window = self.find_client_widget(self.client_view, "Window")

    def test_set_title(self):
        """ Test the setting of a Window's title attribute.
        """
        self.server_window.title = "something else"
        assert self.client_window.title == self.server_window.title

