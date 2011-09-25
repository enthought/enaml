#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from . import send_wx_event

from ..common.radio_button import TestRadioButton


class TestWxRadioButton(TestRadioButton):
    """ WXRadioButton tests. """
    
    def test_initial_value(self):
        """ Test the initial checked state of the radio buttons.
        
        """
        radio1 = self.widget_by_id('radio1')
        widget1 = radio1.toolkit_widget()
        radio2 = self.widget_by_id('radio2')
        widget2 = radio2.toolkit_widget()

        widget1_value = widget1.GetValue()
        self.assertTrue(widget1_value)
        self.assertEqual(radio1.checked, widget1_value)

        widget2_value = widget2.GetValue()
        self.assertFalse(widget2_value)
        self.assertEqual(radio2.checked, widget2_value)
        
