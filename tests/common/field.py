#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import abc

from .enaml_test_case import EnamlTestCase


class TestField(EnamlTestCase):
    """ Logic for testing fields.

    Tooklit testcases need to provide the following methods:

    Abstract Methods
    ----------------

    """

    __metaclass__  = abc.ABCMeta

    label_1 = 'Label 1'

    label_2 = 'Label 2'

    enaml = """
Window:
    Panel:
        VGroup:
            Field field:
                max_length = 8
                cursor_position = 1
                placeholder_text = 'hold'

                value = 'abc'

                max_length_reached >> events.append('max_length_reached')
                text_changed >> events.append('text_changed')
                text_edited >> events.append('text_edited')
                return_pressed >> events.append('return_pressed')
"""

    def setUp(self):
        """ Set up tests for Enaml's Field widget.

        """
        super(TestField, self).setUp()
        self.component = self.widget_by_id('field')
        self.widget = self.component.toolkit_widget()

    def test_initial_value(self):
        """ Test the toolkit widget's initial state.
        
        """
        component_string = self.component.to_string(self.component.value)
        self.assertEqual(component_string, self.get_value(self.widget))
        
    def test_send_text(self):
        """ Simulate typing into a field.
        
        """
        self.send_text(self.widget, '!?')
        component_string = self.component.to_string(self.component.value)
        self.assertEqual(component_string, self.get_value(self.widget))
    
    def test_send_twice(self):
        """ Type text, then type more text.
        
        """
        self.send_text(self.widget, 'zz')
        self.test_send_text()
    
    def test_position_cursor(self):
        """ Position the cursor before typing.
        
        """
        self.set_cursor(self.widget, 0)
        self.send_text(self.widget, 'xyz')
        self.assertEqual(self.get_value(self.widget), 'xyzabc')
        
    
    def test_enaml_text_changed(self):
        """ Check that the widget reflects changes to the Enaml component.
        
        """
        self.component.value = 10
        component_string = self.component.to_string(self.component.value)
        self.assertEqual(self.get_value(self.widget), component_string)

    def test_max_length(self):
        """ Check that the field enforces its maximum length.
        
        """
        max_len = self.component.max_length
        self.send_text(self.widget, 'a' * (max_len + 1))
        widget_text = self.get_value(self.widget)
        component_text = self.component.to_string(self.component.value)
        
        self.assertEqual(widget_text, component_text)
        self.assertEqual(len(widget_text), max_len)
        
        # Qt doesn't automatically fire a relevant signal, so it will fail.
        self.assertIn('max_length_reached', self.events)
    
    def test_component_set_selection(self):
        """ Check the Enaml component's text selection feature.
        
        """
        self.component.value = 'text'
        self.component.set_selection(1, 3)
        self.assertEqual(self.component.selected_text, 'ex')
        
    
    # Note: neither backend (wxPython or Qt) seems to support becoming
    # read-only at run time, at least not when setting text programmatically.
    def test_widget_read_only(self):
        """ Check that the toolkit widget enforces its read-only flag.
        
        """
        initial = self.get_value(self.widget)
        self.component.read_only = True
        self.send_text(self.widget, 'foo')
        #self.component.value = 'foo'
        self.assertEqual(self.get_value(self.widget), initial)
    
    def test_to_string(self):
        """ Test the field's 'to_string' attribute.
        
        """
        self.component.value = 5
        self.component.to_string = lambda x: str(x) + '!'
        self.assertEqual(self.get_value(self.widget), '5!')
    
    def test_from_string(self):
        """ Test the field's 'from_string' attribute.
        
        """
        self.component.from_string = lambda x: int(x, 16)
        self.assertEqual(self.component.value, 0xABC)

    #--------------------------------------------------------------------------
    # Test toolkit implementation class's methods
    #--------------------------------------------------------------------------
    def test_clear(self):
        """ Clear all text from the field.
        
        """
        self.clear_text_and_focus(self.widget)
        self.assertEqual(self.component.value, '')

    '''def select_all(self):
        raise NotImplementedError

    def deselect(self):
        raise NotImplementedError
    
    def clear(self):
        raise NotImplementedError

    def backspace(self):
        raise NotImplementedError
    
    def delete(self):
        raise NotImplementedError

    def end(self, mark=False):
        raise NotImplementedError
    
    def home(self, mark=False):
        raise NotImplementedError
    
    def cut(self):
        raise NotImplementedError
    
    def copy(self):
        raise NotImplementedError

    def paste(self):
        raise NotImplementedError
    
    def insert(self, text):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError
    
    def redo(self):
        raise NotImplementedError'''


    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @abc.abstractmethod
    def get_value(self, widget):
        """ Get the visible text of a field.

        """
        return NotImplemented

    @abc.abstractmethod
    def send_text(self, widget, text):
        """ Simulate typing in a field.

        """
        return NotImplemented
        
    
    @abc.abstractmethod    
    def clear_text_and_focus(self, widget):
        """ Clear the field's text, and remove its focus.
        
        """
        return NotImplemented

    @abc.abstractmethod
    def set_cursor(self, widget, index):
        """ Set the cursor at a specific position.
        
        """
        return NotImplemented
