#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestLabel(EnamlTestCase):
    """ Unit tests for the Label widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Label, Window

enamldef MainView(Window):
    Label:
        text = "text"
"""
        self.parse_and_create(enaml_source)
        self.server_label = self.find_server_widget(self.view, "Label")
        self.client_label = self.find_client_widget(self.client_view, "QtLabel")

    def test_set_text(self):
        """ Test the setting of a Label's text attribute.
        """
        with self.app.process_events():
            self.server_label.text = "something else"

        self.assertEquals(self.client_label.text(), self.server_label.text)

    ## Need to add tests for align and vertical_align
