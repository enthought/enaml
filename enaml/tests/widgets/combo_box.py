#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class TestComboBox(EnamlTestCase):
    """ Logic for testing combo boxes.

    Tooklit testcases need to provide the following methods

    Abstract Methods
    ----------------
    get_selected_text(self, widget)
        Get the current selected text of a combo box.

    get_item_text(self, widget, index)
        Get the text of a combo box item at a particular index.

    select_item(self, widget, index)
        Fire an event to simulate the selection of an item.

    """

    def setUp(self):
        """ Setup before the combo box tests.

        """

        enaml = """
enamldef MainView(MainWindow):
    attr events
    ComboBox:
        name = 'cmb'
        items = [int, float, oct]
        value = float
        to_string = lambda x: str(x) + '!' if x is not None else ''
        selected :: events.append(('selected', event.new))
"""

        self.events = []
        self.view = self.parse_and_create(enaml, events=self.events)
        self.component = self.component_by_name(self.view, 'cmb')
        self.widget = self.component.toolkit_widget

    def test_initialization(self):
        """ Test the initial state.

        """
        component = self.component
        str_value = component.selected_text
        self.assertEqual(self.get_selected_text(self.widget), str_value)
        self.assertEqual(component.value, component.items[1])
        self.assertEqual(self.events, [])

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
        component.to_string = lambda x: str(x) + '?'
        self.test_items()

    def test_selected_event(self):
        """ Fire an event for item selection.

        """
        self.select_item(self.widget, 2)
        self.assertEqual(self.events, [('selected', oct)])

    def test_change_selected_item(self):
        """ Update the visible item when a new one is selected internally.

        """
        component = self.component
        self.assertEqual(component.value, float)
        index = 2
        self.select_item(self.widget, index)
        self.assertEqual(component.value, oct)
        self.assertEqual(self.events, [('selected', oct)])

    def test_append_item(self):
        """ Add an item on the Enaml side; see if the toolkit widget 
        updates.

        """
        component = self.component
        component.items.append('hello')
        self.test_items()

    def test_remove_item(self):
        """ Remove an item on the Enaml side; see if the toolkit widget 
        updates.

        """
        component = self.component
        component.items.pop(0)
        self.test_items()

    def test_deselect(self):
        """ Assert that an invalid value sets the index to -1.

        """
        component = self.component
        component.value = hex
        self.assertTrue(component.value is hex)
        self.assertEqual(component.index, -1)

    def test_value_when_items_change(self):
        """ Assert that the selection moves correctly when the items 
        change.

        """
        component = self.component
        component.value = int
        self.assertEqual(component.value, int)
        self.assertEqual(component.index, 0)
        component.items.insert(0, hex)
        self.assertEqual(component.index, 1)
        self.assertEqual(self.events, [])

    def test_index_when_items_change(self):
        """ Assert that the index is -1 when the value is removed from 
        the items list.

        """
        component = self.component
        component.value = int
        component.items.pop(0)
        self.assertEqual(component.index, -1)
        self.assertEqual(self.events, [])

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_selected_text(self, widget):
        """ Get the current selected text of a combo box.

        """
        pass

    @required_method
    def get_item_text(self, widget, index):
        """ Get the text of a combo box item at a particular index.

        """
        pass

    @required_method
    def select_item(self, widget, index):
        """ Fire an event to simulate the selection of an item.

        """
        pass

