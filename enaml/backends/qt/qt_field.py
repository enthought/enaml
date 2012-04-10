#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Signal
from .qt.QtGui import QLineEdit
from .qt_control import QtControl
from .qt_enaml_validator import QtEnamlValidator

from ...components.field import AbstractTkField
from ...guard import guard


_PASSWORD_MODES = {
    'normal': QLineEdit.Normal,
    'password': QLineEdit.Password,
    'silent': QLineEdit.NoEcho,
}


class QtEnamlLineEdit(QLineEdit):
    """ A QLineEdit subclass which converts a lost focus event into 
    a lost focus signal.

    """
    lostFocus = Signal()

    def focusOutEvent(self, event):
        self.lostFocus.emit()
        return super(QtEnamlLineEdit, self).focusOutEvent(event)


class QtField(QtControl, AbstractTkField):
    """ A Qt implementation of a Field which uses a QLineEdit to provide
    a single line of editable text.

    """
    #--------------------------------------------------------------------------
    # SetupMethods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QLineEdit.

        """
        self.widget = QtEnamlLineEdit(parent)

    def initialize(self):
        """ Initializes the attributes of the Qt widget.

        """
        super(QtField, self).initialize()
        shell = self.shell_obj
        self.set_validator(shell.validator)
        self.set_read_only(shell.read_only)
        self.set_placeholder_text(shell.placeholder_text)
        self.set_text(shell.validator.format(shell.value))
        self.set_cursor_position(shell.cursor_position)
        self.set_password_mode(shell.password_mode)
        self.set_max_length(shell.max_length)
        
    def bind(self):
        """ Binds the event handlers for the QLineEdit.

        """
        super(QtField, self).bind()
        widget = self.widget
        widget.textEdited.connect(self.on_text_edited)
        widget.returnPressed.connect(self.on_return_pressed)
        widget.lostFocus.connect(self.on_lost_focus)
        widget.selectionChanged.connect(self.on_selection_changed)
        widget.cursorPositionChanged.connect(self.on_cursor_changed)

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #-------------------------------------------------------------------------- 
    def shell_validator_changed(self, validator):
        """ The change handler for the 'validator' attribute on the 
        shell object.
        
        """
        self.set_validator(validator)
           
    def shell_max_length_changed(self, max_length):
        """ The change handler for the 'max_length' attribute on the 
        shell object.

        """
        self.set_max_length(max_length)

    def shell_read_only_changed(self, read_only):
        """ The change handler for the 'read_only' attribute on the
        shell object.

        """
        self.set_read_only(read_only)

    def shell_cursor_position_changed(self, cursor_position):
        """ The change handler for the 'cursor_position' attribute on 
        the shell object.

        """
        if not guard.guarded(self, 'updating_cursor'):
            self.set_cursor_position(cursor_position)

    def shell_placeholder_text_changed(self, placeholder_text):
        """ The change handler for the 'placeholder_text' attribute on
        the shell object.

        """
        self.set_placeholder_text(placeholder_text)

    def shell_password_mode_changed(self, mode):
        """ The change handler for the 'password_mode' attribute on the 
        shell object.
        
        """
        self.set_password_mode(mode)

    #--------------------------------------------------------------------------
    # Manipulation Methods 
    #--------------------------------------------------------------------------
    def set_selection(self, start, end):
        """ Sets the selection to the bounds of start and end.

        If the indices are invalid, no selection will be made, and any
        current selection will be cleared.

        Arguments
        ---------
        start : Int
            The start selection index, zero based.

        end : Int
            The end selection index, zero based.

        """
        self.widget.setSelection(start, end - start)

    def select_all(self):
        """ Select all the text in the field.

        If there is no text in the field, the selection will be empty.

        """
        self.widget.selectAll()

    def deselect(self):
        """ Deselect any selected text.

        """
        self.widget.deselect()

    def clear(self):
        """ Clear the field of all text.

        """
        self.widget.clear()

    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left of 
        the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.backspace()

    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right of 
        the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.del_()

    def end(self, mark=False):
        """ Moves the cursor to the end of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to the 
            end of the field. Defaults to False.

        """
        widget = self.widget
        if mark:
            start = widget.cursorPosition()
            end = len(widget.text())
            widget.setSelection(start, end)
        else:
            widget.end(mark)

    def home(self, mark=False):
        """ Moves the cursor to the beginning of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to the 
            beginning of the field. Defaults to False.

        """
        widget = self.widget
        if mark:
            start = 0
            end = widget.cursorPosition()
            widget.setSelection(start, end)
        else:
            widget.home(mark)

    def cut(self):
        """ Cuts the selected text from the field.

        Copies the selected text to the clipboard then deletes the 
        selected text from the field.

        """
        self.widget.cut()

    def copy(self):
        """ Copies the selected text to the clipboard.

        """
        self.widget.copy()

    def paste(self):
        """ Paste the contents of the clipboard into the field.

        Inserts the contents of the clipboard into the field at the 
        current cursor position, replacing any selected text.

        """
        self.widget.paste()

    def insert(self, text):
        """ Insert the text into the field.

        Inserts the given text into the field at the current cursor 
        position, replacing any selected text.

        Arguments
        ---------
        text : str
            The text to insert into the field.

        """
        self.widget.insert(text)

    def undo(self):
        """ Undoes the last operation.

        """
        self.widget.undo()

    def redo(self):
        """ Redoes the last operation.

        """
        self.widget.redo()

    #--------------------------------------------------------------------------
    # Signal Handlers 
    #--------------------------------------------------------------------------
    def on_text_edited(self):
        """ The signal handler for the 'textEdited' signal. This is
        called when the user edits the text via the ui.

        """
        self.shell_obj._field_text_edited()

    def on_return_pressed(self):
        """ The signal handler for the returnPressed signal.

        """
        self.shell_obj._field_return_pressed()

    def on_lost_focus(self):
        """ The signal handler for the lostFocus signal.

        """
        self.shell_obj._field_lost_focus()

    def on_selection_changed(self):
        """ The signal handler for the selectionChanged signal.

        """
        with guard(self, 'updating_selection'):
            self.shell_obj.selected_text = self.widget.selectedText()

    def on_cursor_changed(self):
        """ The event handler for a cursor change event.

        """
        with guard(self, 'updating_cursor'):
            self.shell_obj.cursor_position = self.widget.cursorPosition()

    #--------------------------------------------------------------------------
    # Update methods 
    #--------------------------------------------------------------------------
    def get_text(self):
        """ Returns the current unicode text in the control.

        """
        return self.widget.text()
    
    def set_text(self, text):
        """ Updates the text control with the given unicode text.

        """
        self.widget.setText(text)

    def set_validator(self, validator):
        """ Wraps the given Enaml validator in a custom QValidator 
        instance and applies it to the underlying control.

        """
        qvalidator = QtEnamlValidator(validator)
        self.widget.setValidator(qvalidator)
    
    def set_max_length(self, max_length):
        """ Set the max length of the control to max_length. If the max 
        length is <= 0 or > 32767 then the control will be set to hold 
        32kb of text.

        """
        if (max_length <= 0) or (max_length > 32767):
            max_length = 32767
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

    def set_password_mode(self, password_mode):
        """ Sets the password mode of the wiget.

        """
        self.widget.setEchoMode(_PASSWORD_MODES[password_mode])
        
