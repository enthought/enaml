#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from qt import QtGui

from traits.api import implements, Bool

from .qt_control import QtControl
from ..field import IFieldImpl


class QtField(QtControl):
    """ A Qt implementation of a LineEdit.

    The LineEdit uses a QLineEdit and provides a single line of
    editable text.

    See Also
    --------
    LineEdit

    """
    implements(IFieldImpl)

    #---------------------------------------------------------------------------
    # ILineEditImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QLineEdit.

        """
        self.widget = QtGui.QLineEdit(parent=self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes of the Qt widget.

        """
        parent = self.parent
        self.set_read_only(parent.read_only)
        self.set_placeholder_text(parent.placeholder_text)
        if parent.value:
            self.update_text()
        parent._modified = False
        self.set_cursor_position(parent.cursor_position)
        
        max_length = parent.max_length
        if max_length:
            self.set_max_length(max_length)
        self.bind()

    def parent_max_length_changed(self, max_length):
        """ The change handler for the 'max_length' attribute on the 
        parent.

        """
        self.set_max_length(max_length)

    def parent_read_only_changed(self, read_only):
        """ The change handler for the 'read_only' attribute on the
        parent.

        """
        self.set_read_only(read_only)

    def parent_placeholder_text_changed(self, placeholder_text):
        """ The change handler for the 'placeholder_text' attribute
        on the parent.

        """
        self.set_placeholder_text(placeholder_text)

    def parent_cursor_position_changed(self, cursor_position):
        """ The change handler for the 'cursor_position' attribute on 
        the parent.

        """
        if not self.setting_value:
            self.set_cursor_position(cursor_position)
    
    def parent_converter_changed(self, converter):
        """ Handles the converter object on the parent changing.

        """
        # to_string
        self.update_text()
        
        # from_string
        self.on_text_updated(None)
    
    def parent_value_changed(self, value):
        """ The change handler for the 'value' attribute on the parent.

        """
        if not self.setting_value:
            self.update_text()
            self.parent._modified = False

    def set_selection(self, start, end):
        """ Sets the selection in the widget between the start and 
        end positions, inclusive.

        """
        self.widget.setSelection(start, end - start)
        self.update_parent_selection()

    def select_all(self):
        """ Select all the text in the line edit.

        If there is no text in the line edit, the selection will be
        empty.

        """
        self.widget.selectAll()
        self.update_parent_selection()

    def deselect(self):
        """ Deselect any selected text.

        Sets a selection with start == stop to deselect the current
        selection. The cursor is placed at the beginning of selection.

        """
        self.widget.deselect()
        self.update_parent_selection()

    def clear(self):
        """ Clear the line edit of all text.

        """
        self.widget.clear()
        self.update_parent_selection()

    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left
        of the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.backspace()
        self.update_parent_selection()

    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right
        of the cursor. Otherwise, it deletes the selected text.

        """
        self.widget.del_()
        self.update_parent_selection()

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
        self.update_parent_selection()

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
        self.update_parent_selection()

    def cut(self):
        """ Cuts the selected text from the line edit.

        Copies the selected text to the clipboard then deletes the selected
        text from the line edit.

        """
        self.widget.cut()
        self.update_parent_selection()

    def copy(self):
        """ Copies the selected text to the clipboard.

        """
        self.widget.copy()
        self.update_parent_selection()

    def paste(self):
        """ Paste the contents of the clipboard into the line edit.

        Inserts the contents of the clipboard into the line edit at
        the current cursor position, replacing any selected text.

        """
        self.widget.paste()
        self.update_parent_selection()

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
        self.update_parent_selection()

    def undo(self):
        """ Undoes the last operation.

        """
        self.widget.undo()
        self.update_parent_selection()

    def redo(self):
        """ Redoes the last operation

        """
        self.widget.redo()
        self.update_parent_selection()

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    # A flag which set to True when we're applying updates to the 
    # model. Allows us to avoid unnecessary notification recursion.
    setting_value = Bool(False)

    def bind(self):
        """ Binds the event handlers for the QLineEdit.

        """
        widget = self.widget
        #widget.Bind(wx.EVT_TEXT_MAXLEN, self.on_max_length)
        widget.textChanged.connect(self.on_text_updated) # XXX or should we bind to textEdited?
        widget.returnPressed.connect(self.on_text_enter)
        widget.selectionChanged.connect(self.on_selection)

    def on_text_updated(self, event):
        """ The event handler for the text update event.

        """
        widget = self.widget
        parent = self.parent
        text = widget.text()
        self.setting_value = True
        try:
            value = parent.converter.from_component(text)
        except Exception as e:
            parent.exception = e
            parent.error = True
        else:
            parent.exception = None
            parent.error = False
            parent.value = value
        self.setting_value = False
        self.update_parent_selection()
        parent.text_edited = text
        parent._modified = True
        parent.text_changed = text

    def on_text_enter(self):
        """ The event handler for the return pressed event.

        """
        self.parent.return_pressed = True

    def on_max_length(self, event):
        """ The event handler for the max length event.

        """
        self.parent.max_length_reached = True

    def on_selection(self):
        """ The event handler for a selection (really a left up) event.

        """
        self.update_parent_selection()

    def update_parent_selection(self):
        """ Updates the selection and cursor position of the parent
        to reflect the current state of the widget.

        """
        parent = self.parent
        widget = self.widget
        parent._selected_text = widget.selectedText()
        self.setting_value = True
        parent.cursor_position = widget.cursorPosition()
        self.setting_value = False

    def update_text(self):
        """ Updates the text control with the converted parent value or
        sets the error state on the parent if the conversion fails.

        """
        parent = self.parent
        try:
            text = parent.converter.to_component(parent.value)
        except Exception as e:
            parent.exception = e
            parent.error = True
        else:
            parent.exception = None
            parent.error = False
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
        self.widget.setPlaceholderText(placeholder_text)

    def set_cursor_position(self, cursor_position):
        """ Sets the cursor position of the widget.

        """
        self.widget.setCursorPosition(cursor_position)

