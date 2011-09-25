#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..common.radio_button import TestRadioButton

class TestQtLabel(TestRadioButton):
    """ QtRadioButton tests. """
    
    def test_initial_value(self):
        """ Test the initial checked state of the radio buttons.
        
        """
        radio1 = self.widget_by_id('radio1')
        widget1 = radio1.toolkit_widget()
        radio2 = self.widget_by_id('radio2')
        widget2 = radio2.toolkit_widget()

        widget1_value = widget1.isChecked()
        self.assertTrue(widget1_value)
        self.assertEqual(radio1.checked, widget1_value)

        widget2_value = widget2.isChecked()
        self.assertFalse(widget2_value)
        self.assertEqual(radio2.checked, widget2_value)
