#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from enaml.widgets.wx.tests.utility import EnamlTestCase

class testWXRadioButton(EnamlTestCase):
    """ Testsuite for WXRadioButton

    """

    enaml = \
"""
Window:
    Panel:
        VGroup:
            RadioButton:
                name = 'radio1'
                text = 'Label 1'
                checked = True
            RadioButton:
                name = 'radio2'
                text = 'Label 2'
"""

    def testInitialContents(self):
        """Check the values of the WXRadioButton"""

        radio1 = self.get_widget('radio1')
        widget1 = radio1.toolkit_widget()
        radio2 = self.get_widget('radio2')
        widget2 = radio2.toolkit_widget()

        # checked
        self.assertTrue(widget1.GetValue(),
            'The first radiobutton should be selected')
        self.assertEqual(radio1.checked, widget1.GetValue(),
            'The checked attribute does not agree with the widget')

        self.assertFalse(widget2.GetValue(),
            'The second radiobutton should not be selected')
        self.assertEqual(radio2.checked, widget2.GetValue(),
            'The checked attribute does not agree with the widget')

        # text
        self.assertEqual('Label 1', widget1.GetLabel(),
            "The widget's label should be 'Label 1' ")
        self.assertEqual(radio1.text, widget1.GetLabel(),
            'The text attribute does not agree with the widget label')

        self.assertEqual('Label 2', widget2.GetLabel(),
            "The widget's label should be 'Label 2' ")
        self.assertEqual(radio2.text, widget2.GetLabel(),
            'The text attribute does not agree with the widget label')

    def testLabelChange(self):
        """Test changing the label of a WXRadioButton"""

        radio2 = self.get_widget('radio2')
        widget2 = radio2.toolkit_widget()

        new_label = 'new_label'
        radio2.text = new_label

        self.assertEqual(new_label, widget2.GetLabel(),
            "The widget's label should be 'new_label' ")
        self.assertEqual(radio2.text, widget2.GetLabel(),
            'The text attribute does not agree with the widget label')

    def testSettingChecked(self):
        """Test selecting a WXRadioButton"""

        radio2 = self.get_widget('radio2')
        widget2 = radio2.toolkit_widget()

        # select second
        radio2.checked = True

        self.assertTrue(widget2.GetValue(),
            'The first radiobutton should be selected')
        self.assertEqual(radio2.checked, widget2.GetValue(),
            'The checked attribute does not agree with the widget')

        # de-select second
        radio2.checked = False

        self.assertFalse(widget2.GetValue(),
            'The first radiobutton should be de-selected')
        self.assertEqual(radio2.checked, widget2.GetValue(),
            'The checked attribute does not agree with the widget')

    @unittest.skip('TODO: propagate the wx event properly')
    def testMultipleRadioButtons(self):
        """Selecting one of a set radiobuttons"""

        radio1 = self.get_widget('radio1')
        widget1 = radio1.toolkit_widget()
        radio2 = self.get_widget('radio2')
        widget2 = radio2.toolkit_widget()

        # select second
        radio2.checked = True

        # The synching of values relies on wx events being propogated.
        # We need to manually dispatch them since we're not currently
        # in the event loop.
        self.window.toolkit_widget().ProcessPendingEvents()

        # The selected radio button is ofcourse aware (we did this)
        self.assertEqual(radio2.checked, widget2.GetValue(),
            'The checked attribute does not agree with the widget')

        # Both the wxwidgets know of the change!
        self.assertTrue(widget2.GetValue(),
            'The first radiobutton should be selected')
        self.assertFalse(widget1.GetValue(),
            'The first radiobutton should be de-selected')

        self.assertEqual(radio1.checked, widget1.GetValue(),
            'The checked attribute does not agree with the widget')


if __name__ == '__main__':
    unittest.main()
