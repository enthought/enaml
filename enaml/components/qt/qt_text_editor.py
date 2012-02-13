#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..text_editor import AbstractTkTextEditor

from ...guard import guard


class QtTextEditor(QtControl, AbstractTkTextEditor):
    """ A Qt implementation of a Field.

    QtTextEditor uses a QPlainTextEdit to provide a simple text editor
    widget.

    """
    #--------------------------------------------------------------------------
    # SetupMethods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QTextEditor.

        """
        self.widget = QtGui.QPlainTextEdit(parent)

    def initialize(self):
        """ Initializes the attributes of the Qt widget.

        """
        super(QtTextEditor, self).initialize()
        shell = self.shell_obj
        shell._modified = False
        self.set_read_only(shell.read_only)
        self.set_cursor_position(shell.cursor_position)
        self.set_anchor_position(shell.anchor_position)
        self.set_wrap_lines(shell.wrap_lines)
        self.set_overwrite(shell.overwrite)

    def bind(self):
        """ Binds the event handlers for the QLineEdit.

        """
        super(QtTextEditor, self).bind()
        widget = self.widget
        widget.textChanged.connect(self.on_text_updated) # XXX or should we bind to textEdited?
        widget.selectionChanged.connect(self.on_selection)
        widget.cursorPositionChanged.connect(self.on_cursor)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_read_only_changed(self, read_only):
        """ The change handler for the 'read_only' attribute on the
        parent.

        """
        self.set_read_only(read_only)

    def shell_cursor_position_changed(self, cursor_position):
        """ The change handler for the 'cursor_position' attribute on 
        the parent.

        """
        if not guard.guarded(self, 'setting_cursor'):
            self.set_cursor_position(cursor_position)

    def shell_anchor_position_changed(self, anchor_position):
        """ The change handler for the 'anchor_position' attribute on 
        the parent.

        """
        if not guard.guarded(self, 'setting_cursor'):
            self.set_anchor_position(anchor_position)
    
    def shell_overwrite_changed(self, overwrite):
        """ The change handler for the 'overwrite' attribute on the 
        parent.

        """
        self.set_overwrite(overwrite)
    
    def shell_wrap_lines_changed(self, wrap_lines):
        """ The change handler for the 'wrap_lines' attribute on the 
        parent.

        """
        self.set_wrap_lines(wrap_lines)

    def set_selection(self, start, end):
        """ Sets the selection in the widget between the start and 
        end positions, inclusive.

        """
        cursor = self.widget.textCursor()
        cursor.setAnchor(start)
        cursor.setPosition(end)
        self.widget.setTextCursor(cursor)
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

        If no text is selected, deletes the character to the left of 
        the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.backspace()
        self.update_shell_selection()

    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right of 
        the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.del_()
        self.update_shell_selection()

    def end(self, mark=False):
        """ Moves the cursor to the end of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to the 
            end of the line edit. Defaults to False.

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
            If True, select the text from the current position to the 
            beginning of the line edit. Defaults to False.

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

        Copies the selected text to the clipboard then deletes the 
        selected text from the line edit.

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

        Inserts the contents of the clipboard into the line edit at the 
        current cursor position, replacing any selected text.

        """
        self.widget.paste()
        self.update_shell_selection()

    def insert(self, text):
        """ Insert the text into the line edit.

        Inserts the given text at the current cursor position, replacing
        any selected text.

        Arguments
        ---------
        text : str
            The text to insert into the line edit.

        """
        self.widget.insertPlainText(text)
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

    def find(self, text, backwards=False, case_sensitive=False, whole_words=False):
        """ Finds the text in the editor and sets the cursor to that 
        position.

        Parameters
        ----------
        text : string
            The text to find in the buffer

        backwards : bool, optional
            If True search starting at the end of the buffer. Defaults
            to False.
        
        case_sensitive : bool, optional
            If True, the text matching is case sensitive. Defaults to 
            False.
        
        whole_words : bool, optional
            If True, only complete words are matched. Defaults to False.

        Returns
        -------
        result : bool
            True if the text was found, False otherwise.
        
        """
        options = QtGui.QTextDocument.FindFlags()
        if backwards:
            options |= QtGui.QTextDocument.FindBackward
        if case_sensitive:
            options |= QtGui.QTextDocument.FindCaseSensitively
        if whole_words:
            options |= QtGui.QTextDocument.FindWholeWords
        return self.widget.find(text, options)

    def on_text_updated(self):
        """ The event handler for the text update event.

        """
        shell = self.shell_obj
        self.update_shell_selection()
        shell._modified = True
        shell.text_edited()
        shell.text_changed()

    def on_selection(self):
        """ The event handler for a selection (really a left up) event.

        """
        self.update_shell_selection()

    def on_cursor(self):
        """ The event handler for a cursor move.

        """
        self.update_shell_selection()

    def update_shell_selection(self):
        """ Updates the selection and cursor position of the parent to 
        reflect the current state of the widget.

        """
        shell = self.shell_obj
        cursor = self.widget.textCursor()
        selected_text = cursor.selectedText()
        selected_text = selected_text.replace(u'\u2029', '\n') # replace unicode line break
        shell._selected_text = selected_text
        with guard(self, 'setting_cursor'):
            shell.cursor_position = cursor.position()
            shell.anchor_position = cursor.anchor()
            shell._cursor_column = cursor.positionInBlock()
            shell._cursor_line = cursor.blockNumber()

    def get_text(self):
        """ Get the text currently in the widget.

        """
        text = self.widget.toPlainText()
        return text

    def set_text(self, text):
        """ Changes the text in the widget without emitted a text 
        updated event. This should be called when the text is changed
        programmatically.

        """
        self.widget.setPlainText(text)
    
    def set_read_only(self, read_only):
        """ Sets read only state of the widget.

        """
        self.widget.setReadOnly(read_only)

    def set_cursor_position(self, cursor_position):
        """ Sets the cursor position of the widget.

        """
        cursor = self.widget.textCursor()
        cursor.setPosition(cursor_position)

    def set_anchor_position(self, anchor_position):
        """ Sets the cursor position of the widget.

        """
        cursor = self.widget.textCursor()
        cursor.setPosition(anchor_position)

    def set_wrap_lines(self, wrap_lines):
        """ Sets the line wrapping of the widget.

        """
        if wrap_lines:
            self.widget.setLineWrapMode(QtGui.QPlainTextEdit.WidgetWidth)
        else:
            self.widget.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)

    def set_overwrite(self, overwrite):
        """ Sets the overwrite mode of the widget.

        """
        self.widget.setOverwriteMode(overwrite)

