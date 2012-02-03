#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class TestPushButton(EnamlTestCase):
    """ Logic for testing push buttons.

    Tooklit testcases need to provide the following methods

    Abstract Methods
    ----------------
    button_pressed(self)
        Press the button programmatically.

    button_released(self)
        Release the button programmatically.

    button_clicked(self)
        Click the button programmatically.

    """

    def setUp(self):
        """ Set up before push button tests.

        """

        enaml_source = """
enamldef MainView(MainWindow):
    attr events
    PushButton:
        name = 'pb1'
        text = 'foo'
        clicked :: events.append('clicked')
        pressed :: events.append('pressed')
        released :: events.append('released')
"""

        self.events = []
        self.view = self.parse_and_create(enaml_source, events=self.events)
        self.component = self.component_by_name(self.view, 'pb1')
        self.widget = self.component.toolkit_widget

    def test_button_pressed(self):
        """ React to a push button press event.

        """
        self.button_pressed()

        events = self.events
        self.assertTrue(self.component.down)
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
        events = self.events
        # Release events are ignored if the button weas not already down
        self.button_released()
        self.assertEqual(events, [])

    def test_press_release_sequence(self):
        """ Verify the even firing when the press-release (nornal) sequence
        is applied.

        """
        events = self.events

        self.button_pressed()
        self.assertTrue(self.component.down)
        self.button_released()
        self.assertFalse(self.component.down)
        self.assertEqual(events.count('pressed'), 1)
        self.assertEqual(events.count('released'), 1)
        self.assertNotIn('clicked', events)

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

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def button_pressed(self):
        """ Press the button programmatically.

        """
        pass

    @required_method
    def button_released(self):
        """ Release the button programmatically.

        """
        pass

    @required_method
    def button_clicked(self):
        """ Click the button programmatically.

        """
        pass

