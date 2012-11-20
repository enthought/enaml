#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys
import unittest


from enaml.qt.qt.QtCore import Qt
from .enaml_test_case import EnamlTestCase


class Test(EnamlTestCase):
    """ Unit tests for the WidgetComponent widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Window, PushButton

enamldef MainView(Window):
    PushButton:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "PushButton")
        self.client_widget = self.find_client_widget(self.client_view, "QtPushButton")

    def test_set_enabled(self):
        """ Test the setting of a WidgetComponent's enabled attribute
        """
        with self.app.process_events():
            self.server_widget.enabled = False
        self.assertEquals(
            self.client_widget.isEnabled(), self.server_widget.enabled
        )

    def test_set_visible(self):
        """ Test the setting of a WidgetComponent's visible attribute
        """
        with self.app.process_events():
            self.server_widget.visible = False

        self.assertEquals(
            self.client_widget.isVisible(), self.server_widget.visible
        )

    def test_set_minimum_size(self):
        """ Test the setting of a WidgetComponent's minimum_size attribute
        """
        with self.app.process_events():
            self.server_widget.minimum_size = (100, 100)

        self.assertEquals(
            self.client_widget.minimumSize().toTuple(),
            self.server_widget.minimum_size
        )

    def test_set_maximum_size(self):
        """ Test the setting of a WidgetComponent's maximum_size attribute
        """
        with self.app.process_events():
            self.server_widget.maximum_size = (250, 250)

        self.assertEquals(
            self.client_widget.maximumSize().toTuple(),
            self.server_widget.maximum_size
        )

    @unittest.skipIf(sys.platform != 'darwin', 'Supported only on MacOSX')
    def test_set_show_focus_rect(self):
        """ Test the setting of a WidgetComponent's show_focus_rect attribute
        """
        with self.app.process_events():
            self.server_widget.show_focus_rect = True

        self.assertEquals(
            self.client_widget.testAttribute(Qt.WA_MacShowFocusRect),
            self.server_widget.show_focus_rect
        )

    def test_set_bgcolor(self):
        """ Test the setting of a WidgetComponent's bgcolor attribute
        """
        with self.app.process_events():
            self.server_widget.bgcolor = "#FFFFFF"

        assert self.client_widget.backgroundRole() == self.server_widget.bgcolor

    def test_set_fgcolor(self):
        """ Test the setting of a WidgetComponent's fgcolor attribute
        """
        with self.app.process_events():
            self.server_widget.fgcolor = "#000000"

        assert self.client_widget.foregroundRole() == self.server_widget.fgcolor

    def test_set_font(self):
        """ Test the setting of a WidgetComponent's font attribute
        """
        with self.app.process_events():
            self.server_widget.font = "Helvetica-Regular"

        assert self.client_widget.font == self.server_widget.font



if __name__ == '__main__':
    unittest.main()

