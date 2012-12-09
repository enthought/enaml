#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime

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
        self.client_widget = self.find_client_widget(self.client_view, "QtDateSelector")

    def test_set_date_format(self):
        """ Test the setting of a DateSelector's date_format attribute.
        """

        with self.app.process_events():
            self.server_widget.date_format = "%m/%d/%Y"

        self.assertEquals(self.client_widget.displayFormat(), self.server_widget.date_format)


    ### Testing the BoundedDate interface

    def test_set_minimum_and_maximum(self):
        """ Test the setting of a BoundedDate's miminum and maximum attribute.
        """

        with self.app.process_events():
            self.server_widget.minimum = datetime.date.today()
            self.server_widget.maximum = datetime.date.today() + datetime.timedelta(days=7)

        self.assertEquals(
            self.client_widget.minimumDateTime().toPython().date(), datetime.date.today()
        )
        self.assertEquals(
            self.client_widget.minimumDateTime().toPython().date(), self.server_widget.minimum
        )
        self.assertEquals(
            self.client_widget.maximumDateTime().toPython().date(), self.server_widget.maximum
        )

    def test_set_maximum_with_date_update(self):
        """ Test the setting of a BoundedDate's maximum attribute having an impact on the
        current date selected.
        """

        maximum_date =  datetime.date.today() - datetime.timedelta(days=7)

        with self.app.process_events():
            self.server_widget.maximum = maximum_date

        self.assertEquals(self.client_widget.date().toPython(), maximum_date)

    # XXX: Need to test the receive_date_changed() method

if __name__ == '__main__':
    import unittest
    unittest.main()
