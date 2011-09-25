#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from .enaml_test_case import EnamlTestCase

        
class TestPushButton(EnamlTestCase):
    """ Logic for testing push buttons. """
    
    enaml = """
Window:
    Panel:
        VGroup:
            PushButton pb1:
                text = 'foo'
                clicked >> events.append('clicked')
                pressed >> events.append('pressed')
                released >> events.append('released')
"""
    
    def setUp(self):
        """ Set up push button tests.
        
        """
        super(TestPushButton, self).setUp()
        component = self.widget_by_id('pb1')
        self.widget = component.toolkit_impl.widget
        self.component = component
    
    def button_pressed(self):
        """ React to a push button press event.
        
        """
        events = self.events
        self.assertIn('pressed', events)
        self.assertNotIn('released', events)
        self.assertNotIn('clicked', events)
    
    def button_clicked(self):
        """ Test a push button click event.
        
        """
        events = self.events
        self.assertIn('clicked', events)
        self.assertNotIn('pressed', events)
        self.assertNotIn('released', events)
    
    def button_released(self):
        """ Test a push button release event.
        
        """
        self.assertEqual(self.events, [])

    def button_all_events(self):
        """ Test press, release, and click events.
        
        """
        events = self.events
        self.assertEqual(events.count('clicked'), 1)
        self.assertEqual(events.count('pressed'), 1)
        self.assertEqual(events.count('released'), 1)
