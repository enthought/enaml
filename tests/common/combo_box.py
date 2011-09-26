#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase


class TestComboBox(EnamlTestCase):
    """ Logic for testing combo boxes. """

    enaml = """
Window:
    Panel:
        VGroup:
            ComboBox cmb:
                items = [int, float, oct]
                value = self.items[1]
                to_string = lambda x: str(x) + '!' if x is not None else ''
                selected >> events.append('selected')
"""

    def setUp(self):
        """ Set up combo box tests.

        """
        super(TestComboBox, self).setUp()
        component = self.widget_by_id('cmb')
        self.widget = component.toolkit_widget()
        self.component = component

    def test_selection(self):
        """ Test the initial checked state of the radio buttons.

        """
        component = self.component
        str_value = component.to_string(component.value)
        self.assertEqual(self.get_selected_text(self.widget), str_value)
        self.assertEqual(component.value, component.items[1])

    def test_items(self):
        """ Check that the Enaml combo box items match the toolkit widget.
        
        """
        component = self.component
        for i, item in enumerate(component.items):
            widget_text = self.get_item_text(self.widget, i)
            self.assertEqual(widget_text, component.to_string(item))

    def test_to_string(self):
        """ Update the ComboBox.to_string callable.
        
        """
        component = self.component
        component.to_string = lambda x: str(x) + '?' if x is not None else ''
        self.test_items()

    def test_selected_event(self):
        """ Fire an event for item selection.
        
        """
        self.select_item(self.widget, 2)
        self.assertEqual(self.events, ['selected'])

    def test_change_selected_item(self):
        """ Update the visible item when a new one is selected internally.
        
        """
        component = self.component
        index = 2
        self.select_item(self.widget, index)
        value = component.to_string(component.value)
        self.assertEqual(value, component.to_string(component.items[index]))

    def test_append_item(self):
        """ Add an item on the Enaml side; see if the toolkit widget updates.
        
        """
        component = self.component
        component.items.append('hello')
        self.test_items()

    def test_remove_item(self):
        """ Remove an item on the Enaml side; see if the toolkit widget updates.
        
        """
        component = self.component
        component.items.pop(0)
        self.test_items()
