#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from .enaml_test_case import EnamlTestCase

        
class TestRadioButton(EnamlTestCase):
    """ Logic for testing radio buttons. """
    
    enaml = """
Window:
    Panel:
        VGroup:
            RadioButton radio1:
                text = 'Label 1'
                checked = True
            RadioButton radio2:
                text = 'Label 2'
"""

if __name__ == '__main__':
    unittest.main()
