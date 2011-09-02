# -*- coding: utf-8 -*-
import unittest
import weakref


import wx
import traits.trait_errors

from enaml.widgets.wx.wx_slider import WXSlider
from enaml.enums import Orientation


class WidgetParent(object):
    """Mock parent class"""

    def __init__(self):

        self.app = wx.App(0)
        self.widget = wx.Frame(None)

    def __call__(self):
        return weakref.ref(self)


class testWXSlider(unittest.TestCase):
    """Testsuite for WXSlider

    The widget is tested in isolation without the enaml boilerplate
    """

    def setUp(self):
        # setup an empty application
        parent = WidgetParent()

        # setup widgets

        self.slider = WXSlider()

        # simulating initialization
        self.slider.parent_ref = parent()
        self.slider.create_widget()
        self.slider.tick_interval = 0.1
        self.slider.value = 0.5
        self.slider.init_attributes()

    def checkValue(self, value):
        """Check if the position is correct at the widget and the enaml
        object"""

        widget = self.slider.toolkit_widget()

        self.assertEqual(value, self.slider.value)
        position = self.slider.to_slider(value)
        self.assertEqual(position, self.slider.slider_pos)
        self.assertEqual(round(position / self.slider.tick_interval),
                                                            widget.GetValue())

    def testInitialContents(self):
        """Check the initial values of the WXslider"""

        # down
        self.assertFalse(self.slider.down)

        # position
        self.checkValue(0.5)

        # tick interval
        self.assertEqual(0.1, self.slider.tick_interval)

        # orientation
        self.assertEqual(self.slider.orientation, Orientation.DEFAULT)


    def testValue(self):
        """Test changing the slider value programmaticaly"""

        # minimum
        self.slider.value = 0
        self.checkValue(0)

        # maximum
        self.slider.value = 1
        self.checkValue(1)

        # other
        self.slider.value = 0.3
        self.checkValue(0.3)
        self.slider.value = 0.879
        self.checkValue(0.879)

        # invalid
        self.slider.value = -0.2
        self.checkValue(0.879) #  check that it has not changed the values
        self.slider.value = 3
        self.checkValue(0.879) #  check that it has not changed the values

    def testOrientation(self):
        """Test changing the widget orientation"""

        self.slider.orientation = Orientation.VERTICAL

        self.assertEqual(self.slider.orientation, Orientation.VERTICAL)


if __name__ == '__main__':
    unittest.main()
