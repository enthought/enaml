#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.widgets.label import Label

from .enaml_test_case import EnamlTestCase
from .mock_async_application import MockApplication, find_widget


class TestLabel(EnamlTestCase):
    def setUp(self):
        enaml_source = """
from enaml.widgets import Label, Window

enamldef MainView(Window):
    Label:
        text = "text"
"""
        self.app = MockApplication()
        self.view = self.parse_and_create(enaml_source)
        self.view.prepare()

        for child in self.view.children:
            if isinstance(child, Label):
                self.server_label = child
        self.client_label = find_widget(self.app.builder().root, "Label")

    def test_set_text(self):
        """ Test the setting of a Label's text attribute.
        """
        set_val = "something else"
        self.server_label.text = set_val
        assert self.client_label.text == set_val


