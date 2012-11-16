#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import datetime

from .enaml_test_case import EnamlTestCase


class TestBoundedDatetime(EnamlTestCase):
    """ Unit tests for the BoundedDatetime widget.

    """

    def setUp(self):
        enaml_source = """
from datetime import datetime
from enaml.widgets import BoundedDatetime, Window

minimum_datetime = datetime(1970,1,1, 0,0,0)
maximum_datetime = datetime.now()
other_datetime = datetime(1980, 4, 11, 10, 35, 0)

enamldef MainView(Window):
    BoundedDatetime:
        datetime = other_datetime
        max_datetime = maximum_datetime
        min_datetime = minimum_datetime
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "BoundedDatetime")
        self.client_widget = self.find_client_widget(self.client_view, "BoundedDatetime")

    def test_set_datetime(self):
        """ Test the setting of a BoundedDatetime's datetime attribute.
        """
        self.server_widget.datetime = datetime(2000,1,1,0,0,0)
        assert self.client_widget.datetime == self.server_widget.datetime

    def test_set_max_datetime(self):
        """ Test the setting of a BoundedDatetime's max_datetime attribute.
        """
        self.server_widget.max_datetime = datetime.now()
        assert self.client_widget.max_datetime == self.server_widget.max_datetime

    def test_set_min_datetime(self):
        """ Test the setting of a BoundedDatetime's min_datetime attribute.
        """
        self.server_widget.min_datetime = datetime(1000,1,1,0,0,0)
        assert self.client_widget.min_datetime == self.server_widget.min_datetime

