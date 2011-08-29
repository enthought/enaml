# -*- coding: utf-8 -*-
import unittest
import weakref

import wx

from traitsml.widgets.wx.wx_check_box import WXCheckBox


class WidgetParent(object):
    """Mock parent class"""

    def __init__(self):

        self.app = wx.App(0)
        self.widget = wx.Frame(None)

    def __call__(self):
        return weakref.ref(self)


class testWXRadioButton(unittest.TestCase):
    """Testsuite for WXCheckBox

    The widget is tested in isolation without the traitaml boilerplate
    """

    def setUp(self):
        # setup an empty application
        parent = WidgetParent()

        # setup widgets

        self.checkbox = WXCheckBox()
        self.checkbox.parent_ref = parent()
        self.checkbox.create_widget()
        self.checkbox.init_attributes()

        self.checkbox_label = 'test checkbox'
        self.checkbox.text = self.checkbox_label
        self.checkbox.checked = False
        self.checkbox.widget.SetSize((100, 20))
        self.checkbox.widget.SetPosition((20, 30))

    def testInitialContents(self):
        """Check the values of the WXCheckBox"""

        # checked
        self.assertFalse(self.checkbox.widget.GetValue(),
            'The checkbox should not be checked')
        self.assertEqual(self.checkbox.checked,
            self.checkbox.widget.GetValue(),
            'The checked attribute does not agree with the widget')

        # text
        self.assertEqual(self.checkbox_label, self.checkbox.widget.GetLabel(),
            "The widget's label should be {0}".format(self.checkbox_label))
        self.assertEqual(self.checkbox.text, self.checkbox.widget.GetLabel(),
            'The text attribute does not agree with the widget label')

    def testLabelChange(self):
        """Test changing the label of a WXCheckBox"""

        new_label = 'new_label'
        self.checkbox.text = new_label

        self.assertEqual(new_label, self.checkbox.widget.GetLabel(),
            "The widget's label should be {0}".format(new_label))
        self.assertEqual(self.checkbox.text, self.checkbox.widget.GetLabel(),
            'The text attribute does not agree with the widget label')

    def testSettingChecked(self):
        """Test selecting a WXCheckBox"""

        # un-check
        self.checkbox.checked = False

        self.assertFalse(self.checkbox.widget.GetValue(),
            'The checkbox should be unchecked')
        self.assertEqual(self.checkbox.checked,
            self.checkbox.widget.GetValue(),
            'The checked attribute does not agree with the widget')

        # check
        self.checkbox.checked = True

        self.assertTrue(self.checkbox.widget.GetValue(),
            'The checkbox should be checked')
        self.assertEqual(self.checkbox.checked,
            self.checkbox.widget.GetValue(),
            'The checked attribute does not agree with the widget')


if __name__ == '__main__':
    unittest.main()
