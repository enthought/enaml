#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class Test(EnamlTestCase):
    """ Unit tests for the WidgetComponent widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets.api import Window
from enaml.widgets.widget_component import WidgetComponent

enamldef MainView(Window):
    WidgetComponent:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "WidgetComponent")
        self.client_widget = self.find_client_widget(self.client_view, "WidgetComponent")

    def test_set_enabled(self):
        """ Test the setting of a WidgetComponent's enabled attribute
        """
        self.server_widget.enabled = False
        assert self.client_widget.enabled == self.server_widget.enabled

    def test_set_visible(self):
        """ Test the setting of a WidgetComponent's visible attribute
        """
        #import IPython
        #IPython.embed()
        self.server_widget.visible = False
        assert self.client_widget.visible == self.server_widget.visible

    def test_set_bgcolor(self):
        """ Test the setting of a WidgetComponent's bgcolor attribute
        """
        self.server_widget.bgcolor = "#FFFFFF"
        assert self.client_widget.bgcolor == self.server_widget.bgcolor

    def test_set_fgcolor(self):
        """ Test the setting of a WidgetComponent's fgcolor attribute
        """
        self.server_widget.fgcolor = "#000000"
        assert self.client_widget.fgcolor == self.server_widget.fgcolor

    def test_set_font(self):
        """ Test the setting of a WidgetComponent's font attribute
        """
        self.server_widget.font = "Helvetica-Regular"
        assert self.client_widget.font == self.server_widget.font

    def test_set_minimum_size(self):
        """ Test the setting of a WidgetComponent's min_size attribute
        """
        self.server_widget.minimum_size = (100, 100)
        assert self.client_widget.minimum_size == self.server_widget.minimum_size

    def test_set_maximum_size(self):
        """ Test the setting of a WidgetComponent's max_size attribute
        """
        self.server_widget.maximum_size = (250, 250)
        assert self.client_widget.maximum_size == self.server_widget.maximum_size

    def test_set_show_focus_rect(self):
        """ Test the setting of a WidgetComponent's show_focus_rect attribute
        """
        self.server_widget.show_focus_rect = True
        assert self.client_widget.show_focus_rect == self.server_widget.show_focus_rect

