# -*- coding: utf-8 -*-
import sys

import wx

from traits.api import implements, Bool, Event, Str, Int, Property

from .wx_element import WXElement
from ..i_line_edit import ILineEdit


class WXLineEdit(WXElement):
    """ A wxPython implementation of a single-line editable text widget.

    Attributes
    ----------
    max_length : Int
        The maximum length of the line edit in characters. Default is
        sys.maxint which means there is not limit.

    read_only : Bool
        Whether or not the line edit is read only.

    cursor_position : Int
        The position of the cursor in the line edit.

    modified : Bool
        True if the user has modified the line edit from the ui, False
        otherwise. This is reset to False if the text is programmatically
        changed.

    placeholder_text : Str
        The grayed-out text to display if 'text' is empty and the widget
        doesn't have focus.

    text : String
        The string to use in the line edit. If the length of the new text is
        longer than the maximum length allowed then it is trancated.

    selected_text : Property(Str)
        The text selected in the line edit. This is a read only property that
        is updated whenever the selection changes.

    text_changed : Event
        Fired when the text is changed programmatically, or by the user via
        the ui. The args object will contain the text.

    text_edited : Event
        Fired when the text is changed by the user explicitly through the ui
        and not programmatically. The args object will contain the text.

    return_pressed : Event
        Fired when the return/enter key is pressed in the line edit.

    Methods
    -------
    set_selection(start, end)
        Sets the selection to the bounds of start and end.

    select_all()
        Select all the text in the line edit.

    deselect()
        Deselect any selected text.

    clear()
        Clear the line edit of all text.

    backspace()
        If no text is selected, deletes the character to the left of the
        cursor. Otherwise, it deletes the selected text.

    delete()
        If no text is selected, deletes the character to the right of the
        cursor. Otherwise, it deletes the selected text.

    end(mark=False)
        Moves the cursor to the end of the line. If 'mark' is True, also
        selects the text from the current position to the end.

    home(mark=False)
        Moves the cursor to the beginning of the line. If 'mark' is True,
        also selects the text from the current position to the beginning.

    cut()
        Copies the selected text to the clipboard, then deletes the selected
        text from the line edit.

    copy()
        Copies the selected text to the clipboard.

    paste()
        Inserts the contents of the clipboard into the line edit, replacing
        any selected text.

    insert(text)
        Inserts the given text at the current cursor position, replacing
        any selected text.

    undo()
        Undoes the last operation.

    redo()
        Redoes the last operation.

    """

    implements(ILineEdit)

    #--------------------------------------------------------------------------
    # ILineEdit interface
    #--------------------------------------------------------------------------

    max_length = Int(sys.maxint)

    read_only = Bool

    cursor_position = Int

    modified = Bool

    placeholder_text = Str

    text = Str

    selected_text = Property(Str)

    text_changed = Event

    text_edited = Event

    return_pressed = Event

    #==========================================================================
    # Implementation
    #==========================================================================

    def create_widget(self):
        """Initialization of the IRadionButton based on wxWidget
        """
        # create widget and announce that we want to handle enter events
        widget = wx.TextCtrl(parent=self.parent_widget(),
            style=wx.TE_PROCESS_ENTER)

        # Bind class functions to wx widget events
        widget.Bind(wx.EVT_TEXT_MAXLEN, self._on_max_length)
        widget.Bind(wx.EVT_TEXT, self._on_text_updated)
        widget.Bind(wx.EVT_TEXT_ENTER, self._on_text_enter)

        # associate widget
        self.widget = widget

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------

    def init_attributes(self):
        """initialize WXLineEdit attributes"""

        # set text
        if '' == self.text:
            self.widget.ChangeValue(self.placeholder_text)
        else:
            self.widget.ChangeValue(self.text)

        # set the editable property
        self.widget.SetEditable(not self.read_only)

        # Set initial positions
        pos = len(self.text)
        self.cursor_position = pos

        # Set modified flags
        self.widget.SetModified(False)

    def init_meta_handlers(self):
        """initialize WXLineEdit meta styles"""
        pass

    #--------------------------------------------------------------------------
    # Notification
    #--------------------------------------------------------------------------

    def _text_changed(self):
        # check if the length is valid
        if len(self.text) > self.max_length:
            new_text = self.text[:self.max_length]
            # FIXME: recursive call to fix the length of self.text
            self.text = new_text
            return

        if not self.widget.IsModified():
            self.modified = False

        # reset the modifed flag in the widget
        self.widget.SetModified(False)

        if self.text != self.widget.GetValue():
            self.widget.ChangeValue(self.text)
            self.text_changed = self.text

        return

    def _read_only_changed(self):
        # only update if the value has actually changed
        if self.read_only == self.widget.IsEditable():
            self.widget.SetEditable(not self.read_only)
        return

    def _max_length_changed(self):
        self.widget.SetMaxLength(self.max_length)
        return

    def _cursor_position_changed(self):
        if self.cursor_position != self.widget.GetInsertionPoint():
            self.widget.SetInsertionPoint(self.cursor_position)
        return

    #--------------------------------------------------------------------------
    # Event handlers
    #--------------------------------------------------------------------------

    def _on_max_length(self, event):
        # TODO: do something to show that no more characters are allowed
        event.skip()
        return

    def _on_text_updated(self, event):
        new_text = self.widget.GetValue()
        if self.text != new_text:
            self.modified = True
            self.text = new_text
            self.text_edited = new_text

        self.cursor_position = self.widget.GetInsertionPoint()
        event.Skip()
        return

    def _on_text_enter(self, event):
        self.return_pressed = event
        event.Skip()
        return

    def default_sizer_flags(self):
        return super(WXLineEdit, self).default_sizer_flags().Proportion(1)

    #--------------------------------------------------------------------------
    # Getters and Setters
    #--------------------------------------------------------------------------

    def _get_selected_text(self):
        return self.widget.GetStringSelection()

    #--------------------------------------------------------------------------
    # Selection handlers
    #--------------------------------------------------------------------------

    def set_selection(self, start, end):
        """ Sets the selection to the bounds of start and end.

        If the indices are invalid, no selection will be made,
        and any current selection will be cleared.

        Arguments
        ---------
        start : Int
            The start selection index, zero based.

        end : Int
            The end selection index, zero based.


        """
        self.widget.SetSelection(start, end)
        self.cursor_position = self.widget.GetInsertionPoint()
        return

    def select_all(self):
        """ Select all the text in the line edit.

        If there is no text in the line edit, the selection will be
        empty.

        """
        self.set_selection(-1, -1)
        return

    def deselect(self):
        """ Deselect any selected text.

        Sets a selection with  start == stop to deselect the current
        selection. The cursor is placed at the beginning of selection
        """
        pos = self.widget.GetInsertionPoint()
        self.set_selection(pos, pos)
        return

    def clear(self):
        """ Clear the line edit of all text.
        """
        self.text = ''
        self.cursor_position = 0
        return

    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left
        of the cursor. Otherwise, it deletes the selected text.

        """
        selected = self.selected_text

        if selected == '':
            end = self.cursor_position
            start = end - 1
        else:
            (start, end) = self.widget.GetSelection()

        self.widget.Remove(start, end)
        return

    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right
        of the cursor. Otherwise, it deletes the selected text.

        """
        selected = self.selected_text

        if selected == '':
            start = self.cursor_position
            end = start + 1
        else:
            (start, end) = self.widget.GetSelection()

        self.widget.Remove(start, end)
        return


    def end(self, mark=False):
        """ Moves the cursor to the end of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to the end of
            the line edit and the cursor is not moved. Defaults to False.

        """
        if mark:
            start_position = self.widget.GetInsertionPoint()
            stop_position = self.widget.GetLastPosition()
            self.set_selection(start_position, stop_position)
        else:
            self.cursor_position = self.widget.GetLastPosition()
        return

    def home(self, mark=False):
        """ Moves the cursor to the beginning of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to
            the beginning of the line edit. The cursor is also not moved to
            the beginning. Defaults to False.

        """
        if mark:
            self.set_selection(0, self.widget.GetInsertionPoint())
        else:
            self.cursor_position = 0
        return

    def cut(self):
        """ Cuts the selected text from the line edit.

        Copies the selected text to the clipboard then deletes the selected
        text from the line edit.

        """
        self.widget.Cut()
        return

    def copy(self):
        """ Copies the selected text to the clipboard.

        .. note:: works under motif and ms windows

        """
        self.widget.Copy()
        return

    def paste(self):
        """ Paste the contents of the clipboard into the line edit.

        Inserts the contents of the clipboard into the line edit at
        the current cursor position, replacing any selected text.

        """
        self.widget.Paste()
        return

    def insert(self, text):
        """ Insert the text into the line edit.

        Inserts the given text at the current cursor position,
        replacing any selected text.

        Arguments
        ---------
        text : str
            The text to insert into the line edit.

        """
        self.widget.WriteText(text)
        return

    def undo(self):
        """ Undoes the last operation.

        """
        self.widget.Undo()
        return

    def redo(self):
        """Redoes the last operation

        """
        self.widget.Redo()
        return
