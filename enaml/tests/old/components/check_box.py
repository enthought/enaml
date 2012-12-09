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

        enaml_source = """
enamldef MainView(MainWindow):
    attr events
    CheckBox:
        name = 'checkb1'
        text = 'checkbox label'
        checked = True
        toggled :: events.append('toggled')
        pressed :: events.append('pressed')
        released :: events.append('released')
""".format(self.check_box_label)

        self.events = []
        self.view = self.parse_and_create(enaml_source, events=self.events)
        self.component = self.component_by_name(self.view, 'checkb1')
        self.widget = self.component.toolkit_widget

    def test_box_initialization(self):
        """ Test the initialization of the widget

        """
        component = self.component
        # checked
        self.assertEnamlInSync(component, 'checked', True)
        self.assertEnamlInSync(component, 'text', self.check_box_label)

    def testLabelChange(self):
        """ Test changing the label of a check box

        """
        component = self.component
        new_label = 'new_label'
        component.text = new_label
        self.assertEnamlInSync(component, 'text', new_label)

    def testSettingChecked(self):
        """ Test selecting a WXCheckBox

        """
        component = self.component
        # un-check
        self.component.checked = False
        self.assertEnamlInSync(component, 'checked', False)
        # check
        self.component.checked = True
        self.assertEnamlInSync(component, 'checked', True)

    def test_checkbox_pressed(self):
        """ React to a checkbox press event.

        """
        events = self.events
        self.checkbox_pressed(self.widget)
        self.assertTrue(self.component.down)
        self.assertEqual(events, ['pressed'])

    def test_checkbox_toggled(self):
        """ Test a checkbox toggled event.

        """
        events = self.events
        self.checkbox_toggle(self.widget)
        self.assertFalse(self.component.down)
        self.assertEqual(events, ['toggled'])

    def test_checkbox_released(self):
        """ Test a checkbox release event.

        """
        events = self.events
        # Release events are ignored if the button was not already down
        self.checkbox_released(self.widget)
        self.assertEqual(events, [])

    def test_press_release_sequence(self):
        """ Verify the even firing when the press-release (nornal) 
        sequence is applied.

        """
        component = self.component
        widget = self.widget
        events = self.events
        self.checkbox_pressed(widget)
        self.assertTrue(component.down)
        self.checkbox_released(widget)
        self.assertFalse(component.down)
        self.assertEqual(events, ['pressed', 'released'])

    def test_checkbox_all_events(self):
        """ Test press, release, and click events.

        """
        self.checkbox_pressed(self.widget)
        self.checkbox_released(self.widget)
        self.checkbox_toggle(self.widget)

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

