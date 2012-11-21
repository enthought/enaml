#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.validation.api import IntValidator

from .enaml_test_case import EnamlTestCase

from enaml.qt.qt_field import ECHO_MODES


class TestField(EnamlTestCase):
    """ Unit tests for the Field widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Field, Window

enamldef MainView(Window):
    Field:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "Field")
        self.client_widget = self.find_client_widget(self.client_view, "QtField")

    def test_set_max_length(self):
        """ Test the setting of a Field's max_length attribute
        """
        with self.app.process_events():
            self.server_widget.max_length = 100

        self.assertEquals(self.client_widget.maxLength(), self.server_widget.max_length)

    def test_set_password_mode(self):
        """ Test the setting of a Field's password_mode attribute
        """
        with self.app.process_events():
            self.server_widget.echo_mode = 'silent'

        self.assertEquals(
            self.client_widget.echoMode(),
            ECHO_MODES[self.server_widget.echo_mode]
        )

    def test_set_placeholder_text(self):
        """ Test the setting of a Field's placeholder_text attribute
        """
        with self.app.process_events():
            self.server_widget.placeholder = "Placeholder"

        self.assertEquals(self.client_widget.placeholderText(), self.server_widget.placeholder)

    def test_set_read_only(self):
        """ Test the setting of a Field's read_only attribute
        """
        with self.app.process_events():
            self.server_widget.read_only = True

        self.assertEquals(self.client_widget.isReadOnly(), self.server_widget.read_only)

    def test_set_submit_mode(self):
        """ Test the setting of a Field's submit_triggers attribute
        """
        with self.app.process_events():
            self.server_widget.submit_triggers = ['lost_focus', 'return_pressed']

        ## Find a way to test that.

    def test_set_validator(self):
        """ Test the setting of a Field's validator attribute
        """
        with self.app.process_events():
            self.server_widget.text = '1'
            self.server_widget.validator = IntValidator()

        assert self.client_widget.validator == self.server_widget.validator

    def test_set_text(self):
        """ Test the setting of a Field's text attribute
        """
        with self.app.process_events():
            self.server_widget.text = "Whatever"

        self.assertEquals(self.client_widget.text(), self.server_widget.text)

