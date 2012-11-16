#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestComboBox(EnamlTestCase):
    """ Unit tests for the ComboBox widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets import ComboBox, Window

enamldef MainView(Window):
    ComboBox:
        items = []
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "ComboBox")
        self.client_widget = self.find_client_widget(self.client_view, "ComboBox")

    def test_set_items(self):
        """ Test the setting of a ComboBox's items attribute
        """
        self.server_widget.items = ["foo", "bar", "baz", "qux"]
        assert self.client_widget.items == self.server_widget.items

    def test_set_value(self):
        """ Test the setting of a ComboBox's value attribute
        """
        self.server_widget.items = ["foo", "bar", "baz"]
        self.server_widget.value = "bar"
        assert self.client_widget.index == self.server_widget.index
        self.server_widget.value = "baz"
        assert self.client_widget.index == self.server_widget.index

