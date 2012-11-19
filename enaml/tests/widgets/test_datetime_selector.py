#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime

from .enaml_test_case import EnamlTestCase

ONE_SECOND_DELTA = datetime.timedelta(seconds=1)

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
        self.client_widget = self.find_client_widget(self.client_view, "QtDatetimeSelector")

    def test_set_date_format(self):
        """ Test the setting of a DateTimeSelector's date_format attribute.
        """

        with self.app.process_events():
            self.server_widget.datetime_format = "%m/%d/%Y"

        self.assertEquals(self.client_widget.displayFormat(), self.server_widget.datetime_format)


    ### Testing the BoundedDate interface

    def test_set_minimum_and_maximum(self):
        """ Test the setting of a BoundedDate's miminum and maximum attribute.
        """

        now = datetime.datetime.now()

        with self.app.process_events():
            self.server_widget.minimum = now
            self.server_widget.maximum = now + datetime.timedelta(days=7)



        self.assertTrue(
            self.client_widget.minimumDateTime().toPython() -  now < ONE_SECOND_DELTA)
        self.assertTrue(
            self.client_widget.minimumDateTime().toPython() - self.server_widget.minimum <  ONE_SECOND_DELTA
        )
        self.assertTrue(
            self.client_widget.maximumDateTime().toPython() - self.server_widget.maximum < ONE_SECOND_DELTA
        )

    def test_set_maximum_with_date_update(self):
        """ Test the setting of a BoundedDate's maximum attribute having an impact on the
        current date selected.
        """

        maximum_date =  datetime.datetime.now() - datetime.timedelta(days=7)

        with self.app.process_events():
            self.server_widget.maximum = maximum_date

        self.assertTrue(
            self.client_widget.dateTime().toPython() - maximum_date < ONE_SECOND_DELTA
        )

    # XXX: Need to test the receive_date_changed() method

if __name__ == '__main__':
    import unittest
    unittest.main()
