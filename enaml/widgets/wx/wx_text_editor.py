#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx.stc

from .wx_control import WXControl

from ..text_editor import AbstractTkTextEditor

from ...guard import guard


class WXTextEditor(WXControl, AbstractTkTextEditor):
    """ A wxPython implementation of a TextEditor.

    WXTextEditor uses the Scintilla-based wx.stc.StyledTextCtrl to provide a
    simple text editor widget.

    """
    #--------------------------------------------------------------------------
    # SetupMethods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.TextCtrl.

        """
        self.widget = wx.stc.StyledTextCtrl(parent)
        self.widget.SetMarginWidth(1, 0)

    def initialize(self):
        """ Initializes the attributes of the Qt widget.

        """
        super(WXTextEditor, self).initialize()
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
        super(WXTextEditor, self).bind()
        widget = self.widget
        widget.Bind(wx.stc.EVT_STC_CHANGE, self.on_text_updated) # XXX or should we bind to textEdited?
        widget.Bind(wx.stc.EVT_STC_UPDATEUI, self.on_selection)


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

    def get_text(self):
        """ Get the text currently in the widget.

        """
        text = self.widget.GetText()
        return text

    def set_text(self, text):
        """ Changes the text in the widget without emitted a text 
        updated event. This should be called when the text is changed
        programmatically.

        """
        self.widget.SetText(text)
    
    def get_selected_text(self):
        """ Get the text currently selected in the widget.

        """
        text = self.widget.GetSelectedText()
        return text

    def set_selection(self, start, end):
        """ Sets the selection in the widget between the start and 
        end positions, inclusive.

        """
        self.widget.SetSelection(start, end)
        self.update_shell_selection()

    def select_all(self):
        self.widget.SelectAll()

    def deselect(self):
        pos = self.shell_obj.cursor_position
        self.widget.SetSelection(pos,pos)

    def clear(self):
        self.widget.clear()

    def backspace(self):
        widget = self.widget
        start, end = widget.GetSelection()
        if start == end:
            start = end - 1
            widget.SetSelection(start, end)
        widget.ReplaceSelection('')
        self._update_shell_selection_and_cursor()

    def delete(self):
        widget = self.widget
        start, end = widget.GetSelection()
        if start == end:
            end = start + 1
            widget.SetSelection(start, end)
        widget.ReplaceSelection('')
        self._update_shell_selection_and_cursor()

    def end(self, mark=False):
        self.widget.End()

    def home(self, mark=False):
        self.widget.Home()

    def cut(self):
        self.widget.Cut()

    def copy(self):
        self.widget.Copy()

    def paste(self):
        self.widget.Paste()

    def insert(self, text):
        self.ReplaceSelection(text)

    def undo(self):
        self.widget.Undo()

    def redo(self):
        self.widget.Redo()
    
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
        widget = self.widget
        old_start, old_end = widget.GetSelection()
        flags = 0
        if case_sensitive:
            flags |= wx.stc.STC_FIND_MATCHCASE
        if case_sensitive:
            flags |= wx.stc.STC_FIND_WHOLEWORD
        if backwards:
            widget.SetSelection(old_start, old_start)
            widget.SearchAnchor()
            start = widget.SearchPrev(flags, text)
        else:
            widget.SetSelection(old_end, old_end)
            widget.SearchAnchor()
            start = widget.SearchNext(flags, text)
        if start == -1:
            widget.SetSelection(old_start, old_end)
            return False
        
        self.set_selection(start, start+len(text))
        return True

    def on_text_updated(self, event):
        """ The event handler for the text update event.

        """
        event.Skip()
        shell = self.shell_obj
        self.update_shell_selection()
        shell._modified = True
        shell.text_edited()
        shell.text_changed()

    def on_selection(self, event):
        """ The event handler for a selection (really a left up) event.

        """
        event.Skip()
        self.update_shell_selection()

    def on_motion(self, event):
        """ The event handler for a selection (really a left up) event.

        """
        event.Skip()
        if event.LeftIsDown() and event.Dragging():
            self.update_shell_selection()

    def on_key_down(self, event):
        """ The event handler for a selection (really a left up) event.

        """
        event.Skip()
        self.update_shell_selection()

    #--------------------------------------------------------------------------
    # Private Methods
    #--------------------------------------------------------------------------
    def update_shell_selection(self):
        """ Updates the selection and cursor position of the parent to 
        reflect the current state of the widget.

        """
        widget = self.widget
        shell = self.shell_obj
        old_selection_length = abs(shell.cursor_position-shell.anchor_position)
        with guard(self, 'setting_cursor'):
            cursor_position = shell.cursor_position = widget.GetCurrentPos()
            shell.anchor_position = widget.GetAnchor()
            shell._cursor_column = widget.GetColumn(cursor_position)
            shell._cursor_line = widget.LineFromPosition(cursor_position)
            # don't fire selection changed when nothing selected before or after
            new_selection_length = abs(shell.cursor_position-shell.anchor_position)
            if not(0 == old_selection_length == new_selection_length):
                shell.selection_changed()

    def set_read_only(self, read_only):
        """ Sets read only state of the widget.

        """
        self.widget.SetReadOnly(read_only)

    def set_cursor_position(self, cursor_position):
        """ Sets the cursor position of the widget.

        """
        self.widget.SetCurrentPos(cursor_position)

    def set_anchor_position(self, anchor_position):
        """ Sets the anchor position of the widget.

        """
        self.widget.SetAnchor(anchor_position)

    def set_wrap_lines(self, wrap_lines):
        """ Sets the line wrapping of the widget.

        """
        if wrap_lines:
            self.widget.SetWrapMode(wx.stc.STC_WRAP_WORD)
        else:
            self.widget.SetWrapMode(wx.stc.STC_WRAP_NONE)

    def set_overwrite(self, overwrite):
        """ Sets the overwrite mode of the widget.

        """
        self.widget.SetOvertype(overwrite)


