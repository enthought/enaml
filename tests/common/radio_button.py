#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from .enaml_test_case import EnamlTestCase

        
class TestRadioButton(EnamlTestCase):
    """ Logic for testing radio buttons. """
    
    label_1 = 'Label 1'
    
    label_2 = 'Label 2'
    
    enaml = """
Window:
    Panel:
        VGroup:
            RadioButton radio1:
                text = '{0}'
                checked = True
            RadioButton radio2:
                text = '{1}'
""".format(label_1, label_2)

    def test_initial_value(self):
        """ Test the initial checked state of the radio buttons.
        
        """
        radio1 = self.widget_by_id('radio1')
        widget1 = radio1.toolkit_widget()
        radio2 = self.widget_by_id('radio2')
        widget2 = radio2.toolkit_widget()

        widget1_value = self.get_value(widget1)
        self.assertTrue(widget1_value)
        self.assertEqual(radio1.checked, widget1_value)

        widget2_value = self.get_value(widget2)
        self.assertFalse(widget2_value)
        self.assertEqual(radio2.checked, widget2_value)

    def test_initial_labels(self):
        radio1 = self.widget_by_id('radio1')
        widget1 = radio1.toolkit_widget()
        radio2 = self.widget_by_id('radio2')
        widget2 = radio2.toolkit_widget()
    
        widget1_label = self.get_text(widget1)
        self.assertEqual(widget1_label, self.label_1)
        self.assertEqual(radio1.text, widget1_label)

        widget2_label = self.get_text(widget2)
        self.assertEqual(widget2_label, self.label_2)
        self.assertEqual(radio2.text, widget2_label)

if __name__ == '__main__':
    unittest.main()
