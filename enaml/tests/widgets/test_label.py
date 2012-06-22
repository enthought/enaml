#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase
from .mock_async_application import MockApplication


class TestLabel(EnamlTestCase):
    def setUp(self):
        enaml_source = """
from enaml.widgets.label import Label
from enaml.widgets.window import Window

enamldef MainView(Window):
    Label:
        text = "text"
"""
        self.app = MockApplication()
        self.view = self.parse_and_create(enaml_source)
        self.view.show()
        self.app.run()

    def test_set_text(self):
        pass

