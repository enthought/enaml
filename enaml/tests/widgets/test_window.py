#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestWindow(EnamlTestCase):
    """ Unit tests for the Window widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Window

enamldef MainView(Window):
    title = ""
"""
        self.parse_and_create(enaml_source)
        self.server_window = self.find_server_widget(self.view, "MainView")
        self.client_window = self.find_client_widget(self.client_view, "MainView")

    def test_set_title(self):
        """ Test the setting of a Window's title attribute.
        """
        assert self.client_window.title == ""
        self.server_window.title = "something else"
        assert self.client_window.title == self.server_window.title

    def test_set_maximize(self):
        """ Test the Window's maximize() method.
        """
        self.server_window.maximize()
        assert hasattr(self.client_window, 'maximize')

    def test_set_minimize(self):
        """ Test the Window's minimize() method.
        """
        self.server_window.minimize()
        assert hasattr(self.client_window, 'minimize')

    def test_set_restore(self):
        """ Test the Window's restore() method.
        """
        self.server_window.restore()
        assert hasattr(self.client_window, 'restore')


if __name__ == '__main__':
    import unittest
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
