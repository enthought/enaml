#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import push_exception_handler, pop_exception_handler

from enaml.validation import IntValidator

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

        enaml_source = """
enamldef MainView(MainWindow):
    attr events
    Field:
        name = 'field'
        max_length = 8
        cursor_position = 1
        placeholder_text = 'hold'
        value = 'abc'
        text_edited :: events.append('text_edited')
        return_pressed :: events.append('return_pressed')
"""

        self.events = []
        self.view = self.parse_and_create(enaml_source, events=self.events)
        self.component = self.component_by_name(self.view, 'field')
        self.gain_focus_if_needed(self.widget)

    @property
    def widget(self):
        """ Get the widget of the main component.

        The property getter is necessary because the internal widget of
        the component might change (see WXField).

        """
        return self.component.toolkit_widget

    def test_value(self):
        """ Test the toolkit widget's initial state.

        """
        self.assertEqual(self.component.value, self.get_value(self.widget))
        self.assertEnamlInSync(self.component, 'value', u'abc')

    def test_edit_text(self):
        """ Simulate typing into a field.

        """
        self.set_cursor_position(self.widget, 1)
        self.edit_text(self.widget, u'!?')
        self.component.submit()
        self.assertEnamlInSync(self.component, 'value', u'a!?bc')

    def test_send_twice(self):
        """ Type text, then type more text.

        """
        self.set_cursor_position(self.widget, 1)
        self.edit_text(self.widget, u'!?')
        self.edit_text(self.widget, u'zz')
        self.component.submit()
        self.assertEnamlInSync(self.component, 'value', u'a!?zzbc')

    def test_position_cursor(self):
        """ Position the cursor before typing.

        """
        self.set_cursor_position(self.widget, 0)
        self.edit_text(self.widget, u'xyz')
        self.component.submit()
        self.assertEqual(self.get_value(self.widget), u'xyzabc')

    def test_enaml_text_changed(self):
        """ Check that the widget reflects changes to the Enaml component.

        """
        self.component.value = u'test'
        self.assertEqual(self.get_value(self.widget), u'test')

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
        self.edit_text(self.widget, u'a' * (max_len + 1))
        self.component.submit()
        self.assertEqual(len(self.component.value), max_len)

    def test_component_set_selection(self):
        """ Check the Enaml component's text selection feature.

        """
        self.component.value = u'text'
        self.component.set_selection(1, 3)
        self.assertEqual(self.component.selected_text, u'ex')

    def test_format(self):
        """ Test the validators formatting.

        """
        self.component.value = 64
        self.component.validator = IntValidator()
        self.assertEqual(self.get_value(self.widget), u'64')

    def test_convert(self):
        """ Test the validators conversion.

        """
        self.component.value = 0
        self.component.validator = IntValidator()
        self.component.clear()
        self.edit_text(self.widget, u'123')
        self.component.submit()
        self.assertEqual(self.component.value, 123)

    def test_validator_change(self):
        """ Check that changing a validator works properly.

        """
        output = [False]
        def handler(obj, name, old, new):
            output[0] = True
        push_exception_handler(handler)
        old = self.component.validator
        self.component.validator = IntValidator()
        self.component.validator = old
        pop_exception_handler()
        self.assertTrue(output[0])

    def test_acceptable(self):
        """ Check that validation properly sets the 'acceptable' attribute.

        """
        self.assertTrue(self.component.acceptable)
        self.component.value = 0
        self.component.validator = IntValidator(low=10, high=150)
        self.assertFalse(self.component.acceptable)
        self.component.clear()
        self.edit_text(self.widget, '100')
        self.assertTrue(self.component.acceptable)
        self.component.clear()
        self.edit_text(self.widget, '5')
        self.assertFalse(self.component.acceptable)

    def test_change_text(self):
        """ Change text programmatically, as opposed to editing it.

        """
        self.change_text(self.widget, 'text')
        self.assertEqual(self.events, [])

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
        self.assertEnamlInSync(self.component, 'selected_text', u'abc')

    def test_deselect(self):
        """ De-select text in a field.

        """
        self.component.select_all()
        self.component.deselect()
        self.assertEnamlInSync(self.component, 'selected_text', u'')

    def test_clear(self):
        """ Clear all text from the field.

        """
        self.component.clear()
        self.assertEqual(self.get_value(self.widget), u'')

    def test_backspace(self):
        """ Test the field's "backspace" method.

        """
        self.set_cursor_position(self.widget, 2)
        self.component.backspace()
        self.assertEqual(self.get_value(self.widget), u'ac')
        self.assertEnamlInSync(self.component, 'cursor_position', 1)

    def test_delete(self):
        """ Test the field's "delete" method.

        """
        self.set_cursor_position(self.widget, 2)
        self.component.delete()
        self.assertEqual(self.get_value(self.widget), u'ab')
        self.assertEnamlInSync(self.component, 'cursor_position', 2)

    def test_end(self, mark=False):
        """ Move the cursor to the end of the field.

        """
        # For some reason, the Qt cursor is getting internally 
        # reset to the end without emitting a signal. I gave up
        # debugging it after 1.5 hours. For now, just trigger 
        # an explicit change. It will probably never show up 
        # as a problem in practice since as soon as you click
        # in the field, the cursor will change. - SCC
        self.component.home()
        self.component.end()
        self.assertEnamlInSync(self.component, 'cursor_position', 3)

    def test_home(self, mark=False):
        """ Move the cursor to the beginning of the field.

        """
        self.component.home()
        self.assertEnamlInSync(self.component, 'cursor_position', 0)

    def test_cut(self):
        """ Remove selected text and add it to the clipboard.

        """
        self.component.set_selection(1, 3)
        self.component.cut()
        self.assertEqual(self.get_value(self.widget), u'a')

    def test_copy_paste(self):
        """ Copy text, then paste it at the beginning of the field.

        """
        self.component.set_selection(1, 2)
        self.component.copy()
        self.set_cursor_position(self.widget, 0)
        self.component.paste()
        self.assertEqual(self.get_value(self.widget), u'babc')

    def test_cut_paste(self):
        """ Cut text, then paste it at the beginning of the field.

        """
        self.component.set_selection(1, 2)
        self.component.cut()
        self.set_cursor_position(self.widget, 0)
        self.component.paste()
        self.assertEqual(self.get_value(self.widget), u'bac')

    def test_insert(self):
        """ Insert text into the field.

        """
        self.set_cursor_position(self.widget, 2)
        self.component.insert('foo')
        self.assertEqual(self.get_value(self.widget), u'abfooc')

    def test_undo_delete(self):
        """ Undo a deletion.

        """
        self.set_cursor_position(self.widget, 1)
        self.component.delete()
        self.assertEqual(self.get_value(self.widget), u'ac')
        self.component.undo()
        self.assertEqual(self.get_value(self.widget), u'abc')

    def test_undo_insert(self):
        """ Undo text insertion.

        """
        self.set_cursor_position(self.widget, 1)
        self.component.insert('bar')
        self.assertEqual(self.get_value(self.widget), u'abarbc')
        self.component.undo()
        self.assertEqual(self.get_value(self.widget), u'abc')

    def test_redo_delete(self):
        """ Redo, after undoing a deletion.

        """
        self.test_undo_delete()
        self.component.redo()
        self.assertEqual(self.get_value(self.widget), u'ac')

    def test_redo_insertion(self):
        """ Redo, after undoing an insertion.

        """
        self.test_undo_insert()
        self.component.redo()
        self.assertEqual(self.get_value(self.widget), u'abarbc')

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_value(self, widget):
        """ Get the visible text of a field.

        """
        pass

    @required_method
    def get_password_mode(self, widget):
        """ Get the password_mode status.

        """
        pass

    @required_method
    def edit_text(self, widget, text):
        """ Simulate typing in a field.

        """
        pass

    @required_method
    def change_text(self, widget, text):
        """ Change text programmatically, rather than "editing" it.

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

    @required_method
    def gain_focus_if_needed(self, widget):
        """ Have the widget gain focus if required for the tests.

        """
        pass

