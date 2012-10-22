#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestDateSelector(EnamlTestCase):
    """ Unit tests for the DateSelector widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import DateSelector, Window

enamldef MainView(Window):
    DateSelector:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "DateSelector")
        self.client_widget = self.find_client_widget(self.client_view, "DateSelector")

    def test_set_date_format(self):
        """ Test the setting of a DateSelector's date_format attribute.
        """
        self.server_widget.date_format = "%m/%d/%Y"
        assert self.client_widget.date_format == self.server_widget.date_format

    # XXX: Need to test the receive_date_changed() method
