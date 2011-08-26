# -*- coding: utf-8 -*-
import unittest

import wx

from ..wx_label import WXSpinCtrl


class WidgetParent(object):
    """Mock parent class"""

    def __init__(self):

        self.app = wx.App(0)
        self.widget = wx.Frame(None)


class testWXSpinCtrl(unittest.TestCase):
    """Testsuite for WXSpinCtrl

    The widget is tested in isolation without the traitaml boilerplate
    """

    def setUp(self):
        # setup an empty application
        parent = WidgetParent()

        # setup widgets
        self.spin_ctrl = WXSpinCtrl()
        self.spin_ctrl.create_widget(parent)
        self.spin_ctrl.init_attributes()

        self.spin_ctrl.min = -10
        self.spin_ctrl.max = 10
    def test_initial_contents(self):
        """Check the text value of the WXLabel"""

        widget = self.label.toolkit_widget()
        self.assertEqual(self.label_text, widget.GetLabel(),
            "The widget's label should be {0}".format(self.label_text))
        self.assertEqual(self.label.text, widget.GetLabel(),
            'The text attribute does not agree with the widget\'s label')

    def test_label_change(self):
        """Test changing the label of a WXLabel"""

        new_label = 'new_label'
        self.label.text = new_label
        widget = self.label.toolkit_widget()

        self.assertEqual(new_label, widget.GetLabel(),
            "The widget's label should be {0}".format(new_label))
        self.assertEqual(self.label.text, widget.GetLabel(),
            'The text attribute does not agree with the widget\'s label')


if __name__ == '__main__':
    unittest.main()
