#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from ..common.radio_button import TestRadioButton

class TestQtLabel(TestRadioButton, unittest.TestCase):
    """ QtRadioButton tests. """
    
    def get_value(self, button):
        """ Get the checked state of a radio button.
        
        """
        return button.isChecked()
        
    def get_text(self, button):
        """ Get the label of a button.
        
        """
        return button.text()
