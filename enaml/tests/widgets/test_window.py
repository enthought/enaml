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
        self.client_window = self.find_client_widget(self.client_view, "QtWindow")

    def test_set_title(self):
        """ Test the setting of a Window's title attribute.
        """
        self.assertEquals(self.client_window.windowTitle(), '')

        with self.app.process_events():
            self.server_window.title = "something else"

        self.assertEquals(self.client_window.windowTitle(), self.server_window.title)

    def test_set_maximize(self):
        """ Test the Window's maximize() method.
        """
        self.assertFalse(self.client_window.isMaximized())

        with self.app.process_events():
            self.server_window.maximize()

        self.assertTrue(self.client_window.isMaximized())

    def test_set_minimize(self):
        """ Test the Window's minimize() method.
        """
        self.assertFalse(self.client_window.isMinimized())

        with self.app.process_events():
            self.server_window.minimize()

        self.assertTrue(self.client_window.isMinimized())

    def test_set_restore(self):
        """ Test the Window's restore() method.
        """
        self.assertFalse(self.client_window.isMinimized())
        with self.app.process_events():
            self.server_window.minimize()
            self.server_window.restore()
        self.assertFalse(self.client_window.isMinimized())


if __name__ == '__main__':
    import unittest
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
