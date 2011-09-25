#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from .enaml_test_case import EnamlTestCase

        
class TestLabel(EnamlTestCase):
    """ Logic for testing labels. """
    
    text = 'foo'
    
    enaml = """
Window:
    Panel:
        VGroup:
            Label label:
                text = '%s'
""" % text
    
    def setUp(self):
        """ Set up label tests.
        
        """
        super(TestLabel, self).setUp()
        component = self.widget_by_id('label')
        self.widget = component.toolkit_impl.widget
        self.component = component
    
    def check_text(self, text):
        """ Check label text.
        
        """
        self.assertEqual(self.component.text, text)
