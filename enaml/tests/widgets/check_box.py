#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method

class TestCheckBox(EnamlTestCase):

    """ Logic for testing push buttons.

    Tooklit testcases need to provide the following functions

    Abstract Methods
    ----------------
    get_text(widget)
        Returns the text from the tookit widget.

    checked_status(widget)
        Returns the checked status of the toolkit widget.

    Checkbox_pressed(self)
        Press the checkbox programmatically.

    Checkbox_released(self)
        Release the checkbox programmatically.

    Checkbox_toggled(self)
        Toggle the button programmatically.

    """


    def setUp(self):
        """ Setup enaml component for testing

        """

        self.check_box_label = 'checkbox label'

        enaml = """
defn MainWindow(events):
    Window:
        CheckBox -> checkb1:
            text = '{0}'
            checked = True
            toggled >> events.append('toggled')
            pressed >> events.append('pressed')
            released >> events.append('released')
""".format(self.check_box_label)

        self.events = []
        self.view = self.parse_and_create(enaml, events=self.events)
        self.component = self.component_by_name(self.view, 'checkb1')
        self.widget = self.component.toolkit_widget

    def test_box_initialization(self):
        """ Test the initialization of the widget

        """
        widget = self.widget
        # checked
        self.assertTrue(self.checked_status(widget),
            'The checkbox should not be checked')
        self.assertEqual(self.component.checked, self.checked_status(widget),
            'The checked attribute does not agree with the widget')

        # text
        self.assertEqual(self.check_box_label, self.get_text(widget),
            "The widget's label should be {0}".format(self.check_box_label))
        self.assertEqual(self.component.text, self.get_text(widget),
            'The text attribute does not agree with the widget label')

    def testLabelChange(self):
        """Test changing the label of a check box

        """

        widget = self.widget
        new_label = 'new_label'
        self.component.text = new_label

        self.assertEqual(new_label, self.get_text(widget),
            "The widget's label should be {0}".format(new_label))
        self.assertEqual(self.component.text, self.get_text(widget),
            'The text attribute does not agree with the widget label')

    def testSettingChecked(self):
        """Test selecting a WXCheckBox"""

        widget = self.widget

        # un-check
        self.component.checked = False

        self.assertFalse(self.checked_status(widget),
            'The checkbox should be unchecked')
        self.assertEqual(self.component.checked,
            self.checked_status(widget),
            'The checked attribute does not agree with the widget')

        # check
        self.component.checked = True

        self.assertTrue(self.checked_status(widget),
            'The checkbox should be unchecked')
        self.assertEqual(self.component.checked,
            self.checked_status(widget),
            'The checked attribute does not agree with the widget')

    def test_checkbox_pressed(self):
        """ React to a checkbox press event.

        """
        self.checkbox_pressed(self.widget)

        events = self.events
        self.assertTrue(self.component.down)
        self.assertIn('pressed', events)
        self.assertNotIn('released', events)
        self.assertNotIn('toggled', events)

    def test_checkbox_toggled(self):
        """ Test a checkbox toggled event.

        """
        self.checkbox_toggle(self.widget)

        events = self.events
        self.assertIn('toggled', events)
        self.assertNotIn('pressed', events)
        self.assertNotIn('released', events)

    def test_checkbox_released(self):
        """ Test a checkbox release event.

        """
        events = self.events
        # Release events are ignored if the button was not already down
        self.checkbox_released(self.widget)
        self.assertEqual(events, [])

    def test_press_release_sequence(self):
        """ Verify the even firing when the press-release (nornal) sequence
        is applied.

        """
        widget = self.widget
        events = self.events

        self.checkbox_pressed(widget)
        self.assertTrue(self.component.down)
        self.checkbox_released(widget)
        self.assertFalse(self.component.down)
        self.assertEqual(events.count('pressed'), 1)
        self.assertEqual(events.count('released'), 1)
        self.assertNotIn('toggled', events)

    def test_checkbox_all_events(self):
        """ Test press, release, and click events.

        """
        self.checkbox_pressed(self.widget)
        self.checkbox_released(self.widget)
        self.checkbox_toggle(self.widget)

        events = self.events
        self.assertEqual(events.count('toggled'), 1)
        self.assertEqual(events.count('pressed'), 1)
        self.assertEqual(events.count('released'), 1)


    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------

    @required_method
    def get_text(self, widget):
        """ Returns the text from the tookit widget.

        """
        pass

    @required_method
    def checked_status(self, widget):
        """ Returns the checked status of the toolkit widget.

        """
        pass

    @required_method
    def checkbox_pressed(self, widget):
        """ Press the checkbox programmatically.

        """
        pass

    @required_method
    def checkbox_released(self, widget):
        """ Release the button programmatically.

        """
        pass

    @required_method
    def checkbox_toggle(self, widget):
        """ Toggle the button programmatically.

        """
        pass

