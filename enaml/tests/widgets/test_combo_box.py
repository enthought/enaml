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
from enaml.widgets.api import ComboBox, Window

enamldef MainView(Window):
    ComboBox:
        items = []
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "ComboBox")
        self.client_widget = self.find_client_widget(
            self.client_view, "QtComboBox"
        )

    def test_set_items(self):
        """ Test the setting of a ComboBox's items attribute. """

        expected_result =  ["foo", "bar", "baz", "qux"]

        with self.app.process_events():
            self.server_widget.items = expected_result

        result = [
            self.client_widget.itemText(i) for i in xrange(self.client_widget.count())
        ]

        self.assertEquals(expected_result, result)

    def test_set_value(self):
        """ Test the setting of a ComboBox's value attribute. """

        with self.app.process_events():
            self.server_widget.items = ["foo", "bar", "baz"]
            self.server_widget.index = 1

        self.assertEquals(self.server_widget.index, self.client_widget.currentIndex())

        with self.app.process_events():
            self.server_widget.index = 2

        self.assertEquals(self.server_widget.index, self.client_widget.currentIndex())

if __name__ == '__main__':
    import unittest
    unittest.main()

