#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestImageView(EnamlTestCase):
    """ Unit tests for the ImageView widget.

    """

    def setUp(self):
        enaml_source = """
from enaml.widgets import ImageView, Window

enamldef MainView(Window):
    ImageView:
        pass
"""
        self.parse_and_create(enaml_source)
        self.server_widget = self.find_server_widget(self.view, "ImageView")
        self.client_widget = self.find_client_widget(self.client_view, "ImageView")

    def test_set_image(self):
        """ Test the setting of a ImageView's image attribute
        """
        # XXX: This needs fleshing out.
        pass

    def test_set_scale_to_fit(self):
        """ Test the setting of a ImageView's scale_to_fit attribute
        """
        self.server_widget.scale_to_fit = False
        assert self.client_widget.scale_to_fit == self.server_widget.scale_to_fit

    def test_set_preserve_aspect_ratio(self):
        """ Test the setting of a ImageView's preserve_aspect_ratio attribute
        """
        self.server_widget.preserve_aspect_ratio = False
        assert self.client_widget.preserve_aspect_ratio == self.server_widget.preserve_aspect_ratio

    def test_set_allow_upscaling(self):
        """ Test the setting of a ImageView's  attribute
        """
        self.server_widget.allow_upscaling = False
        assert self.client_widget.allow_upscaling == self.server_widget.allow_upscaling

