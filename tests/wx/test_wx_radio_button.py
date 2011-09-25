#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

import wx

from . import send_wx_event

from ..common.radio_button import TestRadioButton


class TestWxRadioButton(TestRadioButton, unittest.TestCase):
    """ WXRadioButton tests. """
    
    def get_value(self, button):
        """ Get the checked state of a radio button.
        
        """
        return button.GetValue()
        
    def get_text(self, button):
        """ Get the label of a button.
        
        """
        return button.GetLabel()
    
    def process_events(self, widget):
        """ Process events outside the main event loop.

        """
        widget.ProcessPendingEvents()
