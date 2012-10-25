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
from enaml.widgets.api import Container, Window

enamldef MainView(Window):
    Container:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "Container")
        self.client_widget = self.find_client_widget(self.client_view, "Container")

    def test_set_padding(self):
        """ Test the setting of a Container's padding attribute
        """
        self.server_widget.padding = (0,0,0,0)
        assert hasattr(self.client_widget, 'relayout')

    def test_set_padding_strength(self):
        """ Test the setting of a Container's padding_strength attribute
        """
        self.server_widget.padding_strength = 'ignore'
        assert not hasattr(self.client_widget, 'relayout')

