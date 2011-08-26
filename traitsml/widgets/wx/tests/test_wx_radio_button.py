# -*- coding: utf-8 -*-
import unittest

import wx

from traitsml.widgets.wx.api import WXRadioButton


class WidgetParent(object):
    """Mock parent class"""

    def __init__(self):

        self.app = wx.App(0)
        self.widget = wx.Frame(None)

class testWXRadioButton(unittest.TestCase):
    """Testsuite for WXRadioButton

    The widget is tested in isolation without the traitml boilerplate
    """

    def setUp(self):
        # setup an empty application
        parent = WidgetParent()

        # setup widgets
        # we need more than one for RadioButton since we cannot
        # de-select a single radio button

        self.radio1 = WXRadioButton()
        self.radio1.create_widget(parent)
        self.radio1.init_attributes()

        self.radio2 = WXRadioButton()
        self.radio2.create_widget(parent)
        self.radio2.init_attributes()

        self.radio1.text = 'Label 1'
        self.radio1.widget.SetPosition((20, 10))
        self.radio1.widget.SetSize((100, 20))
        self.radio1.widget.SetWindowStyleFlag(wx.RB_GROUP)
        self.radio1.checked = True

        self.radio2.text = 'Label 2'
        self.radio2.widget.SetSize((100, 20))
        self.radio2.widget.SetPosition((20, 30))

    def testInitialContents(self):
        """Check the values of the WXRadioButton"""

        # checked
        self.assertTrue(self.radio1.widget.GetValue(),
            'The first radiobutton should be selected')
        self.assertEqual(self.radio1.checked, self.radio1.widget.GetValue(),
            'The checked attribute does not agree with the widget')

        self.assertFalse(self.radio2.widget.GetValue(),
            'The second radiobutton should not be selected')
        self.assertEqual(self.radio2.checked, self.radio2.widget.GetValue(),
            'The checked attribute does not agree with the widget')

        # text
        self.assertEqual('Label 1', self.radio1.widget.GetLabel(),
            "The widget's label should be 'Label 1' ")
        self.assertEqual(self.radio1.text, self.radio1.widget.GetLabel(),
            'The text attribute does not agree with the widget label')

        self.assertEqual('Label 2', self.radio2.widget.GetLabel(),
            "The widget's label should be 'Label 2' ")
        self.assertEqual(self.radio2.text, self.radio2.widget.GetLabel(),
            'The text attribute does not agree with the widget label')

    def testLabelChange(self):
        """Test changing the label of a WXRadioButton"""

        new_label = 'new_label'
        self.radio2.text = new_label

        self.assertEqual(new_label, self.radio2.widget.GetLabel(),
            "The widget's label should be 'new_label' ")
        self.assertEqual(self.radio2.text, self.radio2.widget.GetLabel(),
            'The text attribute does not agree with the widget label')

    def testSettingChecked(self):
        """Test selecting a WXRadioButton"""

        # select second
        self.radio2.checked = True

        self.assertTrue(self.radio2.widget.GetValue(),
            'The first radiobutton should be selected')
        self.assertEqual(self.radio2.checked, self.radio2.widget.GetValue(),
            'The checked attribute does not agree with the widget')

        # de-select second
        self.radio2.checked = False

        self.assertFalse(self.radio2.widget.GetValue(),
            'The first radiobutton should be de-selected')
        self.assertEqual(self.radio2.checked, self.radio2.widget.GetValue(),
            'The checked attribute does not agree with the widget')

    @unittest.expectedFailure
    def testMultipleRadioButtons(self):
        """Selecting one of a set radiobuttons

        When wxRadioButtons are in the same group (but not inside a radiobox)
        selecting one of them will automatically deselect the others. Yet
        the other WXRadioButtons will not be aware of the change even thouhg
        the wxWidgets have changed their values.

        """
        # select second
        self.radio2.checked = True

        # The selected radio button is ofcourse aware (we did this)
        self.assertEqual(self.radio2.checked, self.radio2.widget.GetValue(),
            'The checked attribute does not agree with the widget')

        # Both the wxwidgets know of the change!
        self.assertTrue(self.radio2.widget.GetValue(),
            'The first radiobutton should be selected')
        self.assertFalse(self.radio1.widget.GetValue(),
            'The first radiobutton should be de-selected')

        # it will fail here if the decorator is commented out
        self.assertEqual(self.radio1.checked, self.radio1.widget.GetValue(),
            'The checked attribute does not agree with the widget')


if __name__ == '__main__':
    unittest.main()
