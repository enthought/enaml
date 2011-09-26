#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

import wx

from . import process_wx_events

from ..common.radio_button import TestRadioButton


class TestWxRadioButton(TestRadioButton, unittest.TestCase):
    """ WXRadioButton tests. """
    
    def get_value(self, button):
        """ Get the checked state of a radio button.
        
        """
        process_wx_events(self.view.toolkit.app)
        return button.GetValue()
        
    def get_text(self, button):
        """ Get the label of a button.
        
        """
        return button.GetLabel()
    
