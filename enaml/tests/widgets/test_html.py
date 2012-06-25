#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestLabel(EnamlTestCase):
    """ Unit tests for the Html widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets import Html, Window

enamldef MainView(Window):
    Html:
        source = "<html/>"
"""
        self.parse_and_create(enaml_source)
        self.server_label = self.find_server_widget(self.view, "Html")
        self.client_label = self.find_client_widget(self.client_view, "Html")

    def test_set_source(self):
        """ Test the setting of a Html's source attribute.
        """
        self.server_label.source = "<p>Blah"
        assert self.client_label.source == self.server_label.source

