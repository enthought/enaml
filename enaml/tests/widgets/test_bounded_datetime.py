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
from enaml.widgets.api import BoundedDatetime, Window

minimum_datetime = datetime(1970,1,1, 0,0,0)
maximum_datetime = datetime.now()
other_datetime = datetime(1980, 4, 11, 10, 35, 0)

enamldef MainView(Window):
    BoundedDatetime:
        datetime = other_datetime
        maximum = maximum_datetime
        minimum = minimum_datetime
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "BoundedDatetime")
        self.client_widget = self.find_client_widget(self.client_view, "BoundedDatetime")

    def test_set_datetime(self):
        """ Test the setting of a BoundedDatetime's datetime attribute.
        """
        self.server_widget.datetime = datetime(2000,1,1,0,0,0)
        self.assertEquals(self.client_widget.datetime, self.server_widget.datetime.isoformat())

    def test_set_maximum(self):
        """ Test the setting of a BoundedDatetime's maximum attribute.
        """
        self.server_widget.maximum = datetime.now()
        self.assertEquals(self.client_widget.maximum, self.server_widget.maximum.isoformat())

    def test_set_minimum(self):
        """ Test the setting of a BoundedDatetime's minimum attribute.
        """
        self.server_widget.minimum = datetime(1000,1,1,0,0,0)
        self.assertEquals(self.client_widget.minimum, self.server_widget.minimum.isoformat())

