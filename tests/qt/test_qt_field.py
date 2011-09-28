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

    def set_cursor(self, widget, index):
        """ Set the cursor at a specific position.
        
        """
        widget.setCursorPosition(index)

    def get_cursor(self, widget):
        """ Get the cursor position.
        
        """
        return widget.cursorPosition()

    def set_selected_text(self, widget, start, stop):
        """ Select text in a field.
        
        """
        widget.setSelection(start, stop - start)

    def get_selected_text(self, widget):
        """ Get the currently-selected text from a field.
        
        """
        return widget.selectedText()
