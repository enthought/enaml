#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestContainer(EnamlTestCase):
    """ Unit tests for the Container widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Container, Window, Field

enamldef MainView(Window):
    Container:
        hug_width = 'strong'
        hug_height = 'strong'
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "Container")
        self.client_widget = self.find_client_widget(self.client_view, "QtContainer")

    def test_set_padding(self):
        """ Test the setting of a Container's padding attribute
        """

        initial_size = self.client_widget.size().toTuple()

        with self.app.process_events():
            self.server_widget.padding = (0,0,0,0)

        # ensure changing the padding has an impact on the client size. 
        # Removing the padding should make the container larger
        no_padding_size = self.client_widget.size().toTuple()

        self.assertTrue(initial_size[0] < no_padding_size[0])
        self.assertTrue(initial_size[1] < no_padding_size[1])

if __name__ == '__main__':
    import unittest
    unittest.main()
