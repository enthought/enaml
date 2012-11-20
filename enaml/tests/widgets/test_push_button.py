#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestPushButton(EnamlTestCase):
    """ Unit tests for the PushButton widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import PushButton, Window

enamldef Button(PushButton):
    attr click_count = 0


enamldef MainView(Window):
    Button:
        id: pb1
        clicked::
            pb1.click_count += 1
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "Button")
        self.client_widget = self.find_client_widget(self.client_view, "QtPushButton")

    def test_set_text(self):
        """ Test the setting of a PushButton's text attribute
        """

        with self.app.process_events():
            self.server_widget.text = "Push Me!"

        self.assertEquals(self.client_widget.text(), self.server_widget.text)

    def test_client_clicked(self):
        """ Test a click on the client side that must increase the click count on the
        server side.
        """

        initial_click_count = self.server_widget.click_count

        with self.app.process_events():
            self.client_widget.click()

        self.assertEquals(1 + initial_click_count, self.server_widget.click_count)

    def test_server_clicked(self):
        """ Test a click on the client side that must increase the click count on the
        server side.
        """

        initial_click_count = self.server_widget.click_count

        with self.app.process_events():
            self.server_widget.clicked()

        self.assertEquals(1 + initial_click_count, self.server_widget.click_count)



class TestTogglePushButtonControl(EnamlTestCase):
    """ Unit tests for the ToggleControl widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Window, PushButton

enamldef MainView(Window):
    PushButton:
        checkable = True
        checked = False
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "PushButton")
        self.client_widget = self.find_client_widget(self.client_view, "QtPushButton")

    def test_set_checked(self):
        """ Test the setting of a ToggleControl's checked attribute
        """
        with self.app.process_events():
            self.server_widget.checked = not self.server_widget.checked

        self.assertEquals(self.client_widget.isChecked(), self.server_widget.checked)

    def test_client_toggle(self):
        """ Test toggling the state on the client side .
        """

        initial_state = self.server_widget.checked

        with self.app.process_events():
            self.client_widget.toggle()

        self.assertEquals(initial_state, not self.server_widget.checked)

    def test_server_clicked(self):
        """ Test toggling the state on the server side .
        """

        initial_state = self.client_widget.isChecked()

        with self.app.process_events():
            self.server_widget.checked = not initial_state

        self.assertEquals(initial_state, not self.client_widget.isChecked())


if __name__ == '__main__':
    import unittest
    unittest.main()
