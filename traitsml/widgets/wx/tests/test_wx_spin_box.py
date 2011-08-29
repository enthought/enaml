# -*- coding: utf-8 -*-
import unittest
import weakref

import wx

from traitsml.widgets.wx.wx_spin_box import WXSpinBox


class WidgetParent(object):
    """Mock parent class"""

    def __init__(self):

        self.app = wx.App(0)
        self.widget = wx.Frame(None)

    def __call__(self):
        return weakref.ref(self)


class testWXSpinBox(unittest.TestCase):
    """Testsuite for WXSpinBox

    The widget is tested in isolation without the traitaml boilerplate
    """

    def setUp(self):
        # setup an empty application
        parent = WidgetParent()

        # setup widgets
        self.spin_box = WXSpinBox()
        self.spin_box.parent_ref = parent()
        self.spin_box.create_widget()
        self.spin_box.init_attributes()

        self.spin_box.low = -10
        self.spin_box.high = 10
        self.spin_box.value = 2

    def test_initial_contents(self):
        """Check the initial values of the WXSpinBox"""

        widget = self.spin_box.toolkit_widget()
        self.assertEqual(self.spin_box.value, widget.GetValue(),
            "The widget's value should be {0}".format(self.spin_box.value))

    def test_value_change(self):
        """Test changing the value of a WXSpinBox"""

        new_value = -2
        self.spin_box.value = new_value
        widget = self.spin_box.toolkit_widget()

        self.assertEqual(new_value, widget.GetValue(),
            "The widget's value is {0}".format(widget.GetValue()))

    def test_low_change(self):
        """Test changing the low value of a WXSpinBox"""

        new_value = -20
        self.spin_box.low = new_value
        widget = self.spin_box.toolkit_widget()

        self.assertEqual(new_value, widget.GetMin(),
            "The widget's min is {0}".format(widget.GetMin()))

    def test_high_change(self):
        """Test changing the high value of a WXSpinBox"""

        new_value = 20
        self.spin_box.high = new_value
        widget = self.spin_box.toolkit_widget()

        self.assertEqual(new_value, widget.GetMax(),
            "The widget's max is {0}".format(widget.GetMax()))

    def test_validation(self):
        '''Test validation of the range of a WXSpinBox'''

        new_value = 25
        f = lambda: setattr(self.spin_box, 'value', new_value)
        msg = "The value {0} is over the max but was accepted by the widget."
        self.assertRaises(Exception, f, msg.format(new_value))


if __name__ == '__main__':
    unittest.main()
