#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..common import field
from enaml.toolkit import qt_toolkit

class TestQtField(field.TestField):
    """ QtField tests. """

    toolkit = qt_toolkit()

    def get_value(self, widget):
        """ Get the visible text of a field.

        """
        return widget.text()

    def send_text(self, widget, text):
        """ Simulate typing in a field.

        """
        widget.insert(text)
        
        
    def clear_text_and_focus(self, widget):
        """ Clear the field's text, and remove its focus.
        
        """
        widget.clear()
        widget.clearFocus()

    def set_cursor(self, widget, index):
        """ Set the cursor at a specific position.
        
        """
        widget.setCursorPosition(index)
