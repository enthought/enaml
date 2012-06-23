#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.widgets.label import Label

from .enaml_test_case import EnamlTestCase


class TestLabel(EnamlTestCase):
    """ Unit tests for the Label widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets import Label, Window

enamldef MainView(Window):
    Label:
        text = "text"
"""
        self.parse_and_create(enaml_source)
        self.server_label = self.find_server_widget(self.view, "Label")
        self.client_label = self.find_client_widget(self.client_view, "Label")

    def test_set_text(self):
        """ Test the setting of a Label's text attribute.
        """
        self.server_label.text = "something else"
        assert self.client_label.text == self.server_label.text

    def test_set_word_wrap(self):
        """ Test the setting of a Label's word_wrap attribute.
        """
        self.server_label.word_wrap = not self.server_label.word_wrap
        assert self.client_label.word_wrap == self.server_label.word_wrap

