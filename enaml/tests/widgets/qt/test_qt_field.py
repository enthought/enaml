#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import field

class TestQtField(QtTestAssistant, field.TestField):
    """ QtField tests. """

    def get_value(self, widget):
        """ Get the visible text of a field.

        """
        return widget.text()

    def edit_text(self, widget, text):
        """ Simulate typing in a field.

        """
        widget.insert(text)

    def change_text(self, widget, text):
        """ Change text programmatically, rather than "edit" it.

        """
        widget.setText(text)

    def set_cursor_position(self, widget, index):
        """ Set the cursor at a specific position.

        """
        widget.setCursorPosition(index)

    def get_cursor_position(self, widget):
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

    def press_return(self, widget):
        """ Simulate a press of the 'Return' key.

        """
        widget.returnPressed.emit()
