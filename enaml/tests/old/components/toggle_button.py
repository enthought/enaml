#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class TestToggleButton(EnamlTestCase):
    """ Logic for testing toggle buttons.

    Tooklit testcases need to provide the following functions

    Abstract Methods
    ----------------
    get_text(widget)
        Returns the text from the tookit widget.

    checked_status(widget)
        Returns the checked status of the toolkit widget.

    Checkbox_pressed(self)
        Press the toggle button programmatically.

    Checkbox_released(self)
        Release the toggle button programmatically.

    Checkbox_toggled(self)
        Toggle the toggle button programmatically.

    """
    def setUp(self):
        """ Setup enaml component for testing

        """
        self.toggle_button_label = 'toggle button label'

        enaml_source = """
enamldef MainView(MainWindow):
    attr events
    ToggleButton:
        name = 'togglebtn1'
        text = 'toggle button label'
        checked = True
        toggled :: events.append('toggled')
        pressed :: events.append('pressed')
        released :: events.append('released')
""".format(self.toggle_button_label)

        self.events = []
        self.view = self.parse_and_create(enaml_source, events=self.events)
        self.component = self.component_by_name(self.view, 'togglebtn1')
        self.widget = self.component.toolkit_widget

    def test_box_initialization(self):
        """ Test the initialization of the widget

        """
        component = self.component
        # checked
        self.assertEnamlInSync(component, 'checked', True)
        self.assertEnamlInSync(component, 'text', self.toggle_button_label)

    def testLabelChange(self):
        """ Test changing the label of a check box

        """
        component = self.component
        new_label = 'new_label'
        component.text = new_label
        self.assertEnamlInSync(component, 'text', new_label)

    def testSettingChecked(self):
        """ Test selecting a ToggleButton

        """
        component = self.component
        # un-check
        self.component.checked = False
        self.assertEnamlInSync(component, 'checked', False)
        # check
        self.component.checked = True
        self.assertEnamlInSync(component, 'checked', True)

    def test_toggle_button_pressed(self):
        """ React to a toggle button press event.

        """
        events = self.events
        self.toggle_button_pressed(self.widget)
        self.assertTrue(self.component.down)
        self.assertEqual(events, ['pressed'])

    def test_toggle_button_toggled(self):
        """ Test a toggle button toggled event.

        """
        events = self.events
        self.toggle_button_toggle(self.widget)
        self.assertFalse(self.component.down)
        self.assertEqual(events, ['toggled'])

    def test_toggle_button_released(self):
        """ Test a toggle button release event.

        """
        events = self.events
        # Release events are ignored if the button was not already down
        self.toggle_button_released(self.widget)
        self.assertEqual(events, [])

    def test_press_release_sequence(self):
        """ Verify the even firing when the press-release (nornal) 
        sequence is applied.

        """
        component = self.component
        widget = self.widget
        events = self.events
        self.toggle_button_pressed(widget)
        self.assertTrue(component.down)
        self.toggle_button_released(widget)
        self.assertFalse(component.down)
        self.assertEqual(events, ['pressed', 'released'])

    def test_toggle_button_all_events(self):
        """ Test press, release, and click events.

        """
        self.toggle_button_pressed(self.widget)
        self.toggle_button_released(self.widget)
        self.toggle_button_toggle(self.widget)

        events = self.events
        self.assertEqual(events, ['pressed', 'released', 'toggled'])

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_text(self, widget):
        """ Returns the text from the tookit widget.

        """
        pass

    @required_method
    def get_checked(self, widget):
        """ Returns the checked status of the toolkit widget.

        """
        pass

    @required_method
    def toggle_button_pressed(self, widget):
        """ Press the toggle button programmatically.

        """
        pass

    @required_method
    def toggle_button_released(self, widget):
        """ Release the button programmatically.

        """
        pass

    @required_method
    def toggle_button_toggle(self, widget):
        """ Toggle the button programmatically.

        """
        pass

