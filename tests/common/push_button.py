#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
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
        self.widget = component.toolkit_widget()
        self.component = component

    def test_button_pressed(self):
        """ React to a push button press event.

        """
        self.button_pressed()

        events = self.events
        self.assertIn('pressed', events)
        self.assertNotIn('released', events)
        self.assertNotIn('clicked', events)

    def test_button_clicked(self):
        """ Test a push button click event.

        """
        self.button_clicked()

        events = self.events
        self.assertIn('clicked', events)
        self.assertNotIn('pressed', events)
        self.assertNotIn('released', events)

    def test_button_released(self):
        """ Test a push button release event.

        """
        self.button_released()
        self.assertEqual(self.events, [])

    def test_button_all_events(self):
        """ Test press, release, and click events.

        """
        self.button_pressed()
        self.button_released()
        self.button_clicked()

        events = self.events
        self.assertEqual(events.count('clicked'), 1)
        self.assertEqual(events.count('pressed'), 1)
        self.assertEqual(events.count('released'), 1)

    def test_button_down(self):
        """ Test the button's `down` attribute.

        """
        component = self.component

        self.assertFalse(component.down)
        self.button_pressed()
        self.assertTrue(component.down)
        self.button_released()
        self.assertFalse(component.down)
