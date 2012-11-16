#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import date

from .enaml_test_case import EnamlTestCase


class TestBoundedDate(EnamlTestCase):
    """ Unit tests for the BoundedDate widget.

    """

    def setUp(self):
        enaml_source = """
from datetime import date

from enaml.widgets import BoundedDate, Window

minimum_date = date(1970,1,1)
maximum_date = date.today()
current_date = date(1980,4,11)

enamldef MainView(Window):
    BoundedDate:
        min_date = minimum_date
        max_date = maximum_date
        date = current_date
"""
        self.parse_and_create(enaml_source)
        self.server_label = self.find_server_widget(self.view, "BoundedDate")
        self.client_label = self.find_client_widget(self.client_view, "BoundedDate")

    def test_set_date(self):
        """ Test the setting of a BoundedDate's date attribute.
        """
        self.server_label.date = date(1976, 7, 4)
        assert self.client_label.date == self.server_label.date

    def test_set_max_date(self):
        """ Test the setting of a BoundedDate's max_date attribute.
        """
        self.server_label.max_date = date(2525, 1, 1)
        assert self.client_label.max_date == self.server_label.max_date

    def test_set_min_date(self):
        """ Test the setting of a BoundedDate's min_date attribute.
        """
        self.server_label.min_date = date(1900, 1, 1)
        assert self.client_label.min_date == self.server_label.min_date

