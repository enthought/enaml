#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.validation.api import IntValidator

from .enaml_test_case import EnamlTestCase


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
        self.client_widget = self.find_client_widget(self.client_view, "Field")

    def test_set_max_length(self):
        """ Test the setting of a Field's max_length attribute
        """
        self.server_widget.max_length = 100
        assert self.client_widget.max_length == self.server_widget.max_length

    def test_set_password_mode(self):
        """ Test the setting of a Field's password_mode attribute
        """
        self.server_widget.echo_mode = 'silent'
        assert self.client_widget.echo_mode == self.server_widget.echo_mode

    def test_set_placeholder_text(self):
        """ Test the setting of a Field's placeholder_text attribute
        """
        self.server_widget.placeholder = "Placeholder"
        assert self.client_widget.placeholder == self.server_widget.placeholder

    def test_set_read_only(self):
        """ Test the setting of a Field's read_only attribute
        """
        self.server_widget.read_only = True
        assert self.client_widget.read_only == self.server_widget.read_only

    def test_set_submit_mode(self):
        """ Test the setting of a Field's submit_mode attribute
        """
        self.server_widget.submit_triggers = ['return_pressed',]
        assert self.client_widget.submit_triggers == self.server_widget.submit_triggers

    def test_set_validator(self):
        """ Test the setting of a Field's validator attribute
        """
        self.server_widget.text = '1'
        self.server_widget.validator = IntValidator()
        assert self.client_widget.validator == self.server_widget.validator

    def test_set_value(self):
        """ Test the setting of a Field's value attribute
        """
        self.server_widget.text = "Whatever"
        assert self.client_widget.text == self.server_widget.text

