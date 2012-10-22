#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestDatetimeEdit(EnamlTestCase):
    """ Unit tests for the DatetimeEdit widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import DatetimeSelector, Window

enamldef MainView(Window):
    DatetimeSelector:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "DatetimeSelector")
        self.client_widget = self.find_client_widget(self.client_view, "DatetimeSelector")

    def test_set_date_format(self):
        """ Test the setting of a DatetimeEdit's datetime_format attribute.
        """
        self.server_widget.datetime_format = "%m/%d/%Y"
        assert self.client_widget.datetime_format == self.server_widget.datetime_format

    # XXX: Need to test the receive_datetime_changed() method
