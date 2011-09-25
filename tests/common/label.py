#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from .enaml_test_case import EnamlTestCase

        
class TestLabel(EnamlTestCase):
    """ Logic for testing push buttons. """
    
    text = 'foo'
    
    enaml = """
Window:
    Panel:
        VGroup:
            Label label:
                text = '%s'
""" % text
    
    def setUp(self):
        """ Set up push button tests.
        
        """
        super(TestLabel, self).setUp()
        component = self.widget_by_id('label')
        self.widget = component.toolkit_impl.widget
        self.component = component
    
    def check_text(self, text):
        """ React to a push button press event.
        
        """
        self.assertEqual(self.component.text, text)
