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
        items = ["foo", "bar", "baz"]
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "ComboBox")
        self.client_widget = self.find_client_widget(
            self.client_view, "QtComboBox"
        )

    def test_set_items(self):
        """ Test the setting of a ComboBox's items attribute. """

        expected_result =  ["foo", "bar", "baz", "qux"]

        index_before_setting_value = self.server_widget.index

        with self.app.process_events():
            self.server_widget.items = expected_result

        result = [
            self.client_widget.itemText(i) for i in xrange(self.client_widget.count())
        ]

        self.assertEquals(expected_result, result)
        self.assertEquals(index_before_setting_value, self.server_widget.index)


    def test_set_value(self):
        """ Test the setting of a ComboBox's value attribute. """

        self.assertEquals(-1, self.server_widget.index)

        with self.app.process_events():
            self.server_widget.items = ["foo", "bar", "baz"]
            self.server_widget.index = 1

        self.assertEquals(self.server_widget.index, 1)

        self.assertEquals(self.server_widget.index, self.client_widget.currentIndex())

        with self.app.process_events():
            self.server_widget.index = 2

        self.assertEquals(self.server_widget.index, self.client_widget.currentIndex())

        with self.app.process_events():
            self.client_widget.setCurrentIndex(0)

        self.assertEquals(self.server_widget.index, self.client_widget.currentIndex())

    def test_set_value_and_index(self):
        """ Test the setting of a ComboBox's items and  value attribute. """

        self.assertEquals(-1, self.server_widget.index)

        with self.app.process_events():
            self.server_widget.items.append("bb")
            self.server_widget.index = 1

        self.assertEquals(1, self.server_widget.index)

        self.assertEquals(self.server_widget.index, self.client_widget.currentIndex())

class TestComboBoxLoopbackIssue(EnamlTestCase):
    """ A different set of unit tests for the ComboBox widget that are failing
    if the index is not protected on the client side with a loopback_guard

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import ComboBox, Window, PushButton

enamldef MainView(Window):
    ComboBox:
        id: cb
        items = []

    PushButton:
        clicked::
            print 'Clicked'
            cb.items = ['1', '2', '3']
            cb.index = 1
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "ComboBox")
        self.client_widget = self.find_client_widget(
            self.client_view, "QtComboBox"
        )

    def test_set_value(self):
        """ Test the setting of a ComboBox's value attribute with an empty list. 

        Changing the empty list triggers an on_index_changed call on the client
        side that seem to bypass the server set_index call. The problem does not
        happen when the list is not empty.
        """

        with self.app.process_events():
            self.server_widget.items = ["foo", "bar", "baz"]
        with self.app.process_events():
            self.server_widget.index = 1

        self.assertEquals(self.server_widget.index, 1)
        self.assertEquals(self.server_widget.index, self.client_widget.currentIndex())


    def test_set_value_from_button(self):
        """ Test the setting of a ComboBox's value attribute with an empty list. 

        Same test as test_set_value but using a PushButton (closer to reality)
        """

        button = self.find_client_widget(self.client_view, 'QtPushButton')

        with self.app.process_events():
            button.click()

        self.assertEquals(self.client_widget.currentIndex(), 1)
        self.assertEquals(self.server_widget.index, 1)
        self.assertEquals(
            self.server_widget.index, self.client_widget.currentIndex()
        )



if __name__ == '__main__':
    import unittest
    unittest.main()

