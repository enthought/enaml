#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from qt import QtGui

from .qt_control import QtControl

from ..field import AbstractTkField


class QtField(QtControl, AbstractTkField):
    """ A Qt implementation of a Field.

    QtField uses a QLineEdit to provides a single line of editable text.

    """
    # A flag which set to True when we're applying updates to the 
    # model. Allows us to avoid unnecessary notification recursion.
    setting_value = False

    #--------------------------------------------------------------------------
    # SetupMethods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QLineEdit.

        """
        self.widget = QtGui.QLineEdit(parent=self.parent_widget())

    def initialize(self):
        """ Initializes the attributes of the Qt widget.

        """
        super(QtField, self).initialize()
        shell = self.shell_obj
        self.set_read_only(shell.read_only)
        self.set_placeholder_text(shell.placeholder_text)
        
        if shell.value:
            self.update_text()
        
        shell._modified = False
        self.set_cursor_position(shell.cursor_position)
        
        max_length = shell.max_length
        if max_length:
            self.set_max_length(max_length)

    def bind(self):
        """ Binds the event handlers for the QLineEdit.

        """
        super(QtField, self).bind()
        widget = self.widget
        widget.textChanged.connect(self.on_text_updated) # XXX or should we bind to textEdited?
        widget.returnPressed.connect(self.on_text_enter)
        widget.selectionChanged.connect(self.on_selection)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_max_length_changed(self, max_length):
        """ The change handler for the 'max_length' attribute on the 
        parent.

        """
        self.set_max_length(max_length)

    def shell_read_only_changed(self, read_only):
        """ The change handler for the 'read_only' attribute on the
        parent.

        """
        self.set_read_only(read_only)

    def shell_cursor_position_changed(self, cursor_position):
        """ The change handler for the 'cursor_position' attribute on 
        the parent.

        """
        if not self.setting_value:
            self.set_cursor_position(cursor_position)

    def shell_placeholder_text_changed(self, placeholder_text):
        """ The change handler for the 'placeholder_text' attribute
        on the parent.

        """
        self.set_placeholder_text(placeholder_text)

    def shell_converter_changed(self, converter):
        """ Handles the converter object on the parent changing.

        """
        self.update_text()
        self.on_text_updated(None) # XXX - this is a bit smelly
    
    def shell_value_changed(self, value):
        """ The change handler for the 'value' attribute on the parent.

        """
        if not self.setting_value:
            self.update_text()
            self.shell_obj._modified = False

    def set_selection(self, start, end):
        """ Sets the selection in the widget between the start and 
        end positions, inclusive.

        """
        self.widget.setSelection(start, end - start)
        self.update_shell_selection()

    def select_all(self):
        """ Select all the text in the line edit.

        If there is no text in the line edit, the selection will be
        empty.

        """
        self.widget.selectAll()
        self.update_shell_selection()

    def deselect(self):
        """ Deselect any selected text.

        Sets a selection with start == stop to deselect the current
        selection. The cursor is placed at the beginning of selection.

        """
        self.widget.deselect()
        self.update_shell_selection()

    def clear(self):
        """ Clear the line edit of all text.

        """
        self.widget.clear()
        self.update_shell_selection()

    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left
        of the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.backspace()
        self.update_shell_selection()

    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right
        of the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.del_()
        self.update_shell_selection()

    def end(self, mark=False):
        """ Moves the cursor to the end of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to the end of
            the line edit. Defaults to False.

        """
        widget = self.widget
        if mark:
            start = widget.cursorPosition()
            end = len(widget.text())
            widget.setSelection(start, end)
        else:
            widget.end(mark)
        self.update_shell_selection()

    def home(self, mark=False):
        """ Moves the cursor to the beginning of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to
            the beginning of the line edit. Defaults to False.

        """
        widget = self.widget
        if mark:
            start = 0
            end = widget.cursorPosition()
            widget.setSelection(start, end)
        else:
            widget.home(mark)
        self.update_shell_selection()

    def cut(self):
        """ Cuts the selected text from the line edit.

        Copies the selected text to the clipboard then deletes the selected
        text from the line edit.

        """
        self.widget.cut()
        self.update_shell_selection()

    def copy(self):
        """ Copies the selected text to the clipboard.

        """
        self.widget.copy()
        self.update_shell_selection()

    def paste(self):
        """ Paste the contents of the clipboard into the line edit.

        Inserts the contents of the clipboard into the line edit at
        the current cursor position, replacing any selected text.

        """
        self.widget.paste()
        self.update_shell_selection()

    def insert(self, text):
        """ Insert the text into the line edit.

        Inserts the given text at the current cursor position,
        replacing any selected text.

        Arguments
        ---------
        text : str
            The text to insert into the line edit.

        """
        self.widget.insert(text)
        self.update_shell_selection()

    def undo(self):
        """ Undoes the last operation.

        """
        self.widget.undo()
        self.update_shell_selection()

    def redo(self):
        """ Redoes the last operation

        """
        self.widget.redo()
        self.update_shell_selection()

    def on_text_updated(self, event):
        """ The event handler for the text update event.

        """
        widget = self.widget
        shell = self.shell_obj
        text = widget.text()
        self.setting_value = True
        try:
            value = shell.converter.from_component(text)
        except Exception as e:
            shell.exception = e
            shell.error = True
        else:
            shell.exception = None
            shell.error = False
            shell.value = value
        self.setting_value = False
        self.update_shell_selection()
        shell.text_edited = text
        shell._modified = True
        shell.text_changed = text

    def on_text_enter(self):
        """ The event handler for the return pressed event.

        """
        self.shell_obj.return_pressed = True

    def on_max_length(self, event):
        """ The event handler for the max length event.

        """
        self.shell_obj.max_length_reached = True

    def on_selection(self):
        """ The event handler for a selection (really a left up) event.

        """
        self.update_shell_selection()

    def update_shell_selection(self):
        """ Updates the selection and cursor position of the parent
        to reflect the current state of the widget.

        """
        shell = self.shell_obj
        widget = self.widget
        shell._selected_text = widget.selectedText()
        self.setting_value = True
        shell.cursor_position = widget.cursorPosition()
        self.setting_value = False

    def update_text(self):
        """ Updates the text control with the converted parent value or
        sets the error state on the parent if the conversion fails.

        """
        shell = self.shell_obj
        try:
            text = shell.converter.to_component(shell.value)
        except Exception as e:
            shell.exception = e
            shell.error = True
        else:
            shell.exception = None
            shell.error = False
            self.change_text(text)

    def change_text(self, text):
        """ Changes the text in the widget without emitted a text 
        updated event. This should be called when the text is changed
        programmatically.

        """
        self.widget.setText(text)

    def set_max_length(self, max_length):
        """ Sets the max length of the widget to max_length.

        """
        self.widget.setMaxLength(max_length)
    
    def set_read_only(self, read_only):
        """ Sets read only state of the widget.

        """
        self.widget.setReadOnly(read_only)

    def set_placeholder_text(self, placeholder_text):
        """ Sets the placeholder text in the widget.

        """
        self.widget.setPlaceholderText(placeholder_text)

    def set_cursor_position(self, cursor_position):
        """ Sets the cursor position of the widget.

        """
        self.widget.setCursorPosition(cursor_position)

