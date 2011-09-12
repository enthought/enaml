# -*- coding: utf-8 -*-
import unittest
import sys
import weakref

import wx

from enaml.widgets.wx.wx_label import WXLabel


class WidgetParent(object):
    """Mock parent clas"""

    def __init__(self):

        self.app = wx.App(0)
        self.widget = wx.Frame(None)

    def __call__(self):
        return weakref.ref(self)


class testWXLabel(unittest.TestCase):
    """Testsuite for WXLabel

    The widget is tested in isolation without the traitaml boilerplate
    """

    def setUp(self):
        # setup an empty application
        parent = WidgetParent()

        # setup widgets
        self.label = WXLabel()
        self.label.parent_ref = parent()
        self.label.create_widget()
        self.label.init_attributes()

        self.label.text = 'test label'

    def test_initial_contents(self):
        """Check the text value of the WXLabel"""

        self.assertEqual('test label', self.label.widget.GetLabel(),
            "The widget's label should be {0}".format('test label'))
        self.assertEqual(self.label.text, self.label.widget.GetLabel(),
            "The text attribute does not agree with the widget's label")

    @unittest.skipIf(sys.platform.startswith("win"), "Coredump in Windows")
    def test_label_change(self):
        """Test changing the label of a WXLabel"""

        new_label = 'new_label'
        self.label.text = new_label

        self.assertEqual(new_label, self.label.widget.GetLabel(),
            "The widget's label should be {0}".format(new_label))
        self.assertEqual(self.label.text, self.label.widget.GetLabel(),
            "The text attribute does not agree with the widget's label")


if __name__ == '__main__':
    unittest.main()
