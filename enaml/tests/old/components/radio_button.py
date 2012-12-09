#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class TestRadioButton(EnamlTestCase):
    """ Logic for testing radio buttons.

    Tooklit testcases need to provide the following methods

    Abstract Methods
    ----------------
    get_value(self, button)
        Get the checked state of a radio button.

    get_text(self, button)
        Get the label of a button.

    """
    def setUp(self):
        """ Finalise set up before the Radio button tests

        """

        label_1 = 'Label 1'
        label_2 = 'Label 2'

        enaml_source = """
enamldef MainView(MainWindow):
    Container:
        RadioButton:
            name = 'radio1'
            text = '{0}'
            checked = True
        RadioButton:
            name = 'radio2'
            text = '{1}'
""".format(label_1, label_2)

        self.events = []
        self.view = self.parse_and_create(enaml_source)
        self.radio1 = self.component_by_name(self.view, 'radio1')
        self.widget1 = self.radio1.toolkit_widget
        self.radio2 = self.component_by_name(self.view, 'radio2')
        self.widget2 = self.radio2.toolkit_widget

    def test_initial_value(self):
        """ Test the initial checked state of the radio buttons.

        """
        widget1_value = self.get_value(self.widget1)
        self.assertTrue(widget1_value)
        self.assertEqual(self.radio1.checked, widget1_value)

        widget2_value = self.get_value(self.widget2)
        self.assertFalse(widget2_value)
        self.assertEqual(self.radio2.checked, widget2_value)

    def test_initial_labels(self):
        """ Test that the toolkit widget's label reflects the Enaml text.

        """
        widget1_label = self.get_text(self.widget1)
        self.assertEqual(widget1_label, 'Label 1')
        self.assertEqual(self.radio1.text, widget1_label)

        widget2_label = self.get_text(self.widget2)
        self.assertEqual(widget2_label, 'Label 2')
        self.assertEqual(self.radio2.text, widget2_label)

    def test_change_label(self):
        """ Change the label of a RadioButton at the Enaml level.

        """
        new_label = 'new_label'
        self.radio2.text = new_label

        widget2_text = self.get_text(self.widget2)
        self.assertEqual(new_label, widget2_text)
        self.assertEqual(self.radio2.text, widget2_text)

    def test_set_checked(self):
        """ Test setting the value of a radio button in a group.

        """
        # Select the second button.
        self.radio2.checked = True

        widget2_value = self.get_value(self.widget2)
        self.assertTrue(widget2_value)
        self.assertEqual(self.radio2.checked, widget2_value)

        # Select the first button to deselect second.
        self.radio1.checked = True

        widget2_value = self.get_value(self.widget2)
        self.assertFalse(widget2_value)
        self.assertEqual(self.radio2.checked, widget2_value)

    def test_multiple_radio_buttons(self):
        """Test selecting one of a set radiobuttons. """

        # select second
        self.radio2.checked = True

        widget1_value = self.get_value(self.widget1)
        widget2_value = self.get_value(self.widget2)

        # The selected radio button is ofcourse aware (we did this)
        self.assertEqual(self.radio2.checked, widget2_value)

        # Both the wxwidgets know of the change!
        self.assertTrue(widget2_value)
        self.assertFalse(widget1_value)

        self.assertEqual(self.radio1.checked, widget1_value)

    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------
    @required_method
    def get_value(self, button):
        """ Get the checked state of a radio button.

        """
        pass

    @required_method
    def get_text(self, button):
        """ Get the label of a button.

        """
        pass

