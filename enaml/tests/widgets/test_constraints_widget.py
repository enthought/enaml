#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestConstraintsWidget(EnamlTestCase):
    """ Unit tests for the ConstraintsWidget widget. The QtConstraintsWidget
    cannot be instantiated directly. To test the behaviour, we check that
    a Field stored within a Container will be properly updated if we change
    the ConstraintsWidget attribute on the server side.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Window, Field, Container

enamldef MainView(Window):
    initial_size = (500, 100)
    Container:
        Field:
            pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "ConstraintsWidget")
        self.client_widget = self.find_client_widget(self.client_view, "QtConstraintsWidget")

    def test_set_hug(self):
        """ Test the setting of a ConstraintsWidget's hug attribute
        """

        initial_size = self.client_widget.size()

        with self.app.process_events():
            self.server_widget.hug_width = 'ignore'
            self.server_widget.hug_height = 'weak'

        self.assertNotEqual(initial_size, self.client_widget.size())

    def test_set_resist_clip(self):
        """ Test the setting of a ConstraintsWidget's resist_clip attribute
        """


        initial_size = self.client_widget.size()

        with self.app.process_events():
            self.server_widget.resist_width = 'required'
            self.server_widget.resist_height = 'medium'

        self.assertNotEqual(initial_size, self.client_widget.size())


    # XXX Add more tests

if __name__ == '__main__':
    import logging
    import unittest
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
