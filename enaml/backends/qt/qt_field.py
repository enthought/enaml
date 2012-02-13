#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..field import AbstractTkField

from ...guard import guard


_PASSWORD_MODES = {
    'normal': QtGui.QLineEdit.Normal,
    'password': QtGui.QLineEdit.Password,
    'silent': QtGui.QLineEdit.NoEcho,
}


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
        self.widget = QtGui.QLineEdit(parent=parent)

    def initialize(self):
        """ Initializes the attributes of the Qt widget.

        """
        super(QtField, self).initialize()
        shell = self.shell_obj
        self.set_read_only(shell.read_only)
        self.set_placeholder_text(shell.placeholder_text)

        text = shell.field_text
        if text is not None:
            self.set_text(text)
        
        shell._modified = False

        self.set_cursor_position(shell.cursor_position)
        self.set_password_mode(shell.password_mode)
        self.set_max_length(shell.max_length)

    def bind(self):
        """ Binds the event handlers for the QLineEdit.

        """
        super(QtField, self).bind()
        widget = self.widget
        widget.textEdited.connect(self.on_text_edited)
        widget.textChanged.connect(self.on_text_changed)
        widget.returnPressed.connect(self.on_return_pressed)
        widget.selectionChanged.connect(self.on_selection_changed)
        widget.cursorPositionChanged.connect(self.on_cursor_changed)

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
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

    def shell_placeholder_text_changed(self, placeholder_text):
        """ The change handler for the 'placeholder_text' attribute
        on the shell object.

        """
        self.set_placeholder_text(placeholder_text)

    def shell_cursor_position_changed(self, cursor_position):
        """ The change handler for the 'cursor_position' attribute on 
        the shell object.

        """
        if not guard.guarded(self, 'updating_cursor'):
            self.set_cursor_position(cursor_position)

    def shell_field_text_changed(self, text):
        """ The change handler for the 'field_text' attribute on the shell 
        object.

        """
        if text is not None:
            if not guard.guarded(self, 'updating_text'):
                self.set_text(text)
                self.shell_obj._modified = False

    def shell_password_mode_changed(self, mode):
        """ The change handler for the 'password_mode' attribute on the 
        shell object.
        
        """
        self.set_password_mode(mode)

    #--------------------------------------------------------------------------
    # Manipulation Methods 
    #--------------------------------------------------------------------------
    def set_selection(self, start, end):
        """ Sets the selection in the widget between the start and 
        end positions, inclusive.

        """
        self.widget.setSelection(start, end - start)

    def select_all(self):
        """ Select all the text in the line edit.

        If there is no text in the line edit, the selection will be
        empty.

        """
        self.widget.selectAll()

    def deselect(self):
        """ Deselect any selected text.

        Sets a selection with start == stop to deselect the current
        selection. The cursor is placed at the beginning of selection.

        """
        self.widget.deselect()

    def clear(self):
        """ Clear the line edit of all text.

        """
        self.widget.clear()

    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left
        of the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.backspace()

    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right
        of the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.del_()

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

    def cut(self):
        """ Cuts the selected text from the line edit.

        Copies the selected text to the clipboard then deletes the selected
        text from the line edit.

        """
        self.widget.cut()

    def copy(self):
        """ Copies the selected text to the clipboard.

        """
        self.widget.copy()

    def paste(self):
        """ Paste the contents of the clipboard into the line edit.

        Inserts the contents of the clipboard into the line edit at
        the current cursor position, replacing any selected text.

        """
        self.widget.paste()

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

    def undo(self):
        """ Undoes the last operation.

        """
        self.widget.undo()

    def redo(self):
        """ Redoes the last operation

        """
        self.widget.redo()

    #--------------------------------------------------------------------------
    # Signal Handlers 
    #--------------------------------------------------------------------------
    def on_text_edited(self):
        """ The event handler for when the user edits the text through 
        the ui.

        """
        # The textEdited signal will be emitted along with the 
        # textChanged signal if the user edits from the ui. In 
        # that case, we only want to do one update.
        if not guard.guarded(self, 'updating_text'):
            with guard(self, 'updating_text'):
                shell = self.shell_obj
                text = self.widget.text()
                shell.field_text = text
                shell.text_edited(text)
                shell._modified = True

    def on_text_changed(self):
        """ The event handler for when the user edits the text 
        programmatically.

        """
        # The textEdited signal will be emitted along with the 
        # textChanged signal if the user edits from the ui. In 
        # that case, we only want to do one update.
        if not guard.guarded(self, 'updating_text'):
            with guard(self, 'updating_text'):
                shell = self.shell_obj
                text = self.widget.text()
                shell.field_text = text

    def on_return_pressed(self):
        """ The event handler for the return pressed event.

        """
        self.shell_obj.return_pressed()

    def on_selection_changed(self):
        """ The event handler for a selection event.

        """
        with guard(self, 'updating_selection'):
            self.shell_obj._selected_text = self.widget.selectedText()

    def on_cursor_changed(self):
        """ The event handler for a cursor change event.

        """
        with guard(self, 'updating_cursor'):
            self.shell_obj.cursor_position = self.widget.cursorPosition()

    #--------------------------------------------------------------------------
    # Update methods 
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Updates the text control with the new text from the shell
        object.

        """
        self.widget.setText(text)

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
        
