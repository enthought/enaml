#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.converters import Converter, IntConverter

from .enaml_test_case import EnamlTestCase, required_method


class TestField(EnamlTestCase):
    """ Logic for testing fields.

    Tooklit testcases need to provide the following methods:

    Abstract Methods
    ----------------

    """

    def setUp(self):
        """ Set up tests for Enaml's Field widget.

        """

        enaml = """
defn MainWindow(events):
    Window:
        Field -> field:
            max_length = 8
            cursor_position = 1
            placeholder_text = 'hold'

            value = 'abc'

            max_length_reached >> events.append('max_length_reached')
            text_changed >> events.append('text_changed')
            text_edited >> events.append('text_edited')
            return_pressed >> events.append('return_pressed')
"""

        self.events = []
        self.view = self.parse_and_create(enaml, events=self.events)
        self.component = self.component_by_name(self.view, 'field')
        self.widget = self.component.toolkit_widget

    def test_value(self):
        """ Test the toolkit widget's initial state.

        """
        self.assertEqual(self.component.value, self.get_value(self.widget))
        self.assertEnamlInSync(self.component, 'value', 'abc')

    def test_edit_text(self):
        """ Simulate typing into a field.

        """
        self.set_cursor_position(self.widget, 1)
        self.edit_text(self.widget, '!?')
        self.assertEnamlInSync(self.component, 'value', 'a!?bc')

    def test_send_twice(self):
        """ Type text, then type more text.

        """
        self.set_cursor_position(self.widget, 1)
        self.edit_text(self.widget, '!?')
        self.edit_text(self.widget, 'zz')
        self.assertEnamlInSync(self.component, 'value', 'a!?zzbc')

    def test_position_cursor(self):
        """ Position the cursor before typing.

        """
        self.set_cursor_position(self.widget, 0)
        self.edit_text(self.widget, 'xyz')
        self.assertEqual(self.get_value(self.widget), 'xyzabc')

    def test_enaml_text_changed(self):
        """ Check that the widget reflects changes to the Enaml component.

        """
        self.component.value = 'test'
        self.assertEnamlInSync(self.component, 'value', 'test')

    def test_password_mode_silent(self):
        """ Test the password_mode status.

        """
        component = self.component
        component.password_mode = 'silent'
        self.assertEnamlInSync(component, 'password_mode', 'silent')

    def test_password_mode_password(self):
        """ Test the password_mode status.

        """
        component = self.component
        component.password_mode = 'password'
        self.assertEnamlInSync(component, 'password_mode', 'password')

    def test_password_mode_normal(self):
        """ Test the password_mode status.

        """
        component = self.component
        self.assertEnamlInSync(component, 'password_mode', 'normal')
        component.password_mode = 'password' # switch to something else
        component.password_mode = 'normal'
        self.assertEnamlInSync(component, 'password_mode', 'normal')

    def test_max_length(self):
        """ Check that the field enforces its maximum length.

        """
        max_len = self.component.max_length
        self.edit_text(self.widget, 'a' * (max_len + 1))
        widget_text = self.get_value(self.widget)
        self.assertEqual(widget_text, self.component.value)
        self.assertEqual(len(widget_text), max_len)

        # Qt doesn't automatically fire a relevant signal, so it will fail.
        self.assertIn('max_length_reached', self.events)

    def test_component_set_selection(self):
        """ Check the Enaml component's text selection feature.

        """
        self.component.value = 'text'
        self.component.set_selection(1, 3)
        self.assertEqual(self.component.selected_text, 'ex')

    ## Note: When setting text programmatically, neither backend (wxPython
    ## or Qt) seems to support becoming read-only at run time.
    #def test_widget_read_only(self):
    #    """ Check that the toolkit widget enforces its read-only flag.
    #
    #    """
    #    initial = self.get_value(self.widget)
    #    self.component.read_only = True
    #    self.edit_text(self.widget, 'foo')
    #    #self.component.value = 'foo'
    #    self.assertEqual(self.get_value(self.widget), initial)

    def test_convert_to_component(self):
        """ Test the field's 'to_string' attribute.

        """
        self.component.value = 64
        self.component.converter = IntConverter()
        to_component = self.component.converter.to_component
        self.assertEqual(to_component(self.get_value(self.widget)), '64')

    def test_convert_from_component(self):
        """ Test the field's 'from_string' attribute.

        """
        self.change_text(self.widget, '123')
        self.component.converter = IntConverter()
        self.assertEqual(self.component.value, 123)

    def test_conversion_to_and_from_widget(self):
        """ Test a field with both 'to_string' and 'from_string' callables.

        """
        self.component.converter = IntConverter()
        self.component.value = 25
        widget_value = self.get_value(self.widget)
        convert = self.component.converter
        self.assertEqual(convert.to_component(convert.from_component(widget_value)),
                         '25')

    def test_conversion_error(self):
        """ Check that an error is set on a failed conversion.

        """
        self.assertFalse(self.component.error)
        self.change_text(self.widget, '100.0')
        self.component.converter = IntConverter()
        self.assertTrue(self.component.error)

    #def test_placeholder_text(self):
    #    """ Remove focus to check a field's placeholder text.
    #
    #    """
    #    #Not sure how to do this.

    def test_change_text(self):
        """ Change text programmatically, as opposed to editing it.

        """
        self.change_text(self.widget, 'text')
        self.assertEqual(self.events, ['text_changed'])

    def test_press_return(self):
        """ Simulate a press of the 'Return' key.

        """
        self.press_return(self.widget)
        self.assertEqual(self.events, ['return_pressed'])

    #--------------------------------------------------------------------------
    # Test toolkit implementation class's methods
    #--------------------------------------------------------------------------
    def test_select_all(self):
        """ Select all text in a field.

        """
        self.component.select_all()
        self.assertEnamlInSync(self.component, 'selected_text', 'abc')

    def test_deselect(self):
        """ De-select text in a field.

        """
        self.component.select_all()
        self.component.deselect()
        self.assertEnamlInSync(self.component, 'selected_text', '')

    def test_clear(self):
        """ Clear all text from the field.

        """
        self.component.clear()
        self.assertEnamlInSync(self.component, 'value', '')

    def test_backspace(self):
        """ Test the field's "backspace" method.

        """
        self.set_cursor_position(self.widget, 2)
        self.component.backspace()
        self.assertEnamlInSync(self.component, 'value', 'ac')

    def test_delete(self):
        """ Test the field's "delete" method.

        """
        self.set_cursor_position(self.widget, 2)
        self.component.delete()
        self.assertEnamlInSync(self.component, 'value', 'ab')

    def test_end(self, mark=False):
        """ Move the cursor to the end of the field.

        """
        self.component.end()
        self.assertEnamlInSync(self.component, 'cursor_position', 3)

    def test_home(self, mark=False):
        """ Move the cursor to the beginning of the field.

        """
        self.component.home()
        self.assertEnamlInSync(self.component, 'cursor_position', 0)

    # NOTE: The clipboard-related tests sometimes pass, and sometimes fail.

    #def test_cut(self):
    #    """ Remove selected text and add it to the clipboard.
    #
    #    """
    #    self.component.set_selection(1, 3)
    #    self.component.cut()
    #    self.assertEnamlInSync(self.component, 'value', 'a')

    #def test_copy_paste(self):
    #    """ Copy text, then paste it at the beginning of the field.
    #
    #    """
    #    self.component.set_selection(1, 2)
    #    self.component.copy()
    #    self.set_cursor_position(self.widget, 0)
    #    self.component.paste()
    #    self.assertEnamlInSync(self.component, 'value', 'babc')

    #def test_cut_paste(self):
    #    """ Cut text, then paste it at the beginning of the field.
    #
    #    """
    #    self.component.set_selection(1, 2)
    #    self.component.cut()
    #    self.set_cursor_position(self.widget, 0)
    #    self.component.paste()
    #    self.assertEnamlInSync(self.component, 'value', 'bac')

    def test_insert(self):
        """ Insert text into the field.

        """
        self.set_cursor_position(self.widget, 2)
        self.component.insert('foo')
        self.assertEnamlInSync(self.component, 'value', 'abfooc')

    def test_undo_delete(self):
        """ Undo a deletion.

        """
        self.set_cursor_position(self.widget, 1)
        self.component.delete()
        self.assertEnamlInSync(self.component, 'value', 'ac')
        self.component.undo()
        self.assertEnamlInSync(self.component, 'value', 'abc')

    def test_undo_insert(self):
        """ Undo text insertion.

        """
        self.set_cursor_position(self.widget, 1)
        self.component.insert('bar')
        self.assertEnamlInSync(self.component, 'value', 'abarbc')
        self.component.undo()
        self.assertEnamlInSync(self.component, 'value', 'abc')

    def test_redo_delete(self):
        """ Redo, after undoing a deletion.

        """
        self.test_undo_delete()
        self.component.redo()
        self.assertEnamlInSync(self.component, 'value', 'ac')

    def test_redo_insertion(self):
        """ Redo, after undoing an insertion.

        """
        self.test_undo_insert()
        self.component.redo()
        self.assertEnamlInSync(self.component, 'value', 'abarbc')

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_value(self, widget):
        """ Get the visible text of a field.

        """
        pass

    @required_method
    def edit_text(self, widget, text):
        """ Simulate typing in a field.

        """
        pass

    @required_method
    def change_text(self, widget, text):
        """ Change text programmatically, rather than "edit" it.

        """
        pass

    @required_method
    def set_cursor_position(self, widget, index):
        """ Set the cursor at a specific position.

        """
        pass

    @required_method
    def get_cursor_position(self, widget):
        """ Get the cursor position.

        """
        pass

    @required_method
    def get_selected_text(self, widget):
        """ Get the currently-selected text from a field.

        """
        pass

    @required_method
    def press_return(self, widget):
        """ Simulate a press of the 'Return' key.

        """
        pass
