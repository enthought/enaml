#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestConstraintsWidget(EnamlTestCase):
    """ Unit tests for the ConstraintsWidget widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Window
from enaml.widgets.constraints_widget import ConstraintsWidget

enamldef MainView(Window):
    ConstraintsWidget:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "ConstraintsWidget")
        self.client_widget = self.find_client_widget(self.client_view, "ConstraintsWidget")

    def test_set_hug(self):
        """ Test the setting of a ConstraintsWidget's hug attribute
        """
        assert not hasattr(self.client_widget, 'relayout')
        self.server_widget.hug_width = 'ignore'
        self.server.widget.hug_height = 'weak'
        assert hasattr(self.client_widget, 'relayout')

    def test_set_resist_clip(self):
        """ Test the setting of a ConstraintsWidget's resist_clip attribute
        """
        assert not hasattr(self.client_widget, 'relayout')
        self.server_widget.resist_width = 'required'
        self.server_widget.resist_height = 'medium'
        assert hasattr(self.client_widget, 'relayout')

    # XXX Add more tests
