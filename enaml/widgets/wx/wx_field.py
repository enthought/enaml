#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import warnings
import wx
from .wx_control import WXControl
from ..field import AbstractTkField


class CustomTextCtrl(wx.TextCtrl):
    """ A wx.TextCtrl subclass that supports placeholder text.

    This text control will display grayed out provided placeholder text
    when the control is empty and loses focus. As soon as the control
    gains focus, the placeholder text is removed.

    """
    def __init__(self, *args, **kwargs):
        super(CustomTextCtrl, self).__init__(*args, **kwargs)
        self._placeholder_text = ''
        self._placeholder_active = False
        self._user_fgcolor = None
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)

    def SetPlaceHolderText(self, placeholder_text):
        """ Sets the placeholder text to the given value. Pass an empty
        string to turn off the placeholder text functionality.

        """
        self._placeholder_text = placeholder_text
        self.OnKillFocus(None)

    def GetPlaceHolderText(self):
        """ Returns the placeholder text for this control.

        """
        return self._placeholder_text

    def OnKillFocus(self, event):
        """ Handles the kill focus event on the control and refreshes
        the placeholder text if necessary.

        """
        if not self.GetValue() and self._placeholder_text:
            self.ChangeValue(self._placeholder_text)
            color = wx.Color(95, 95, 95)
            super(CustomTextCtrl, self).SetForegroundColour(color)
            self._placeholder_active = True

    def OnSetFocus(self, event):
        """ Handles the on focus event on the control and removes the
        placeholder test if necessary.

        """
        if self._placeholder_active:
            self.ChangeValue('')
            color = self._user_fgcolor or wx.Color(0, 0, 0)
            super(CustomTextCtrl, self).SetForegroundColour(color)
            self._placeholder_active = False

    def GetValue(self):
        """ Returns string value in the control, or an empty string if
        the placeholder text is active.

        """
        if self._placeholder_active:
            return ''
        return super(CustomTextCtrl, self).GetValue()

    def SetForegroundColour(self, wxColor, force=False):
        self._user_fgcolor = wxColor
        if self._placeholder_active and not force:
            return
        super(CustomTextCtrl, self).SetForegroundColour(wxColor)


class WXField(WXControl, AbstractTkField):
    """ A wxPython implementation of a LineEdit.

    The LineEdit uses a custom wx.TextCtrl and provides a single line of
    editable text.

   """
    #: A flag which set to True when we're applying updates to the
    #: model. Allows us to avoid unnecessary notification recursion.
    setting_value = False

    #--------------------------------------------------------------------------
    # SetupMethods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying wx.CustomTextCtrl.

        """
        self.widget = CustomTextCtrl(parent=self.parent_widget(),
                                        style=wx.TE_PROCESS_ENTER)

    def initialize(self):
        """ Initializes the attributes of the wx.CustomTextCtrl.

        """
        super(WXField, self).initialize()
        shell = self.shell_obj
        self.set_max_length(shell.max_length)
        self.set_read_only(shell.read_only)
        self.set_placeholder_text(shell.placeholder_text)
        if shell.value:
            self.update_text()
        shell._modified = False
        self.set_cursor_position(shell.cursor_position)

    def bind(self):
        """ Binds the event handlers for the wx.TextCtrl.

        """
        super(WXField, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_TEXT_MAXLEN, self.on_max_length)
        widget.Bind(wx.EVT_TEXT, self.on_text_updated)
        widget.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter)
        widget.Bind(wx.EVT_LEFT_UP, self.on_selection)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_max_length_changed(self, max_length):
        """ The change handler for the 'max_length' attribute on the
        shell.

        """
        self.set_max_length(max_length)

    def shell_read_only_changed(self, read_only):
        """ The change handler for the 'read_only' attribute on the
        shell.

        """
        self.set_read_only(read_only)

    def shell_placeholder_text_changed(self, placeholder_text):
        """ The change handler for the 'placeholder_text' attribute on
        the shell.

        """
        self.set_placeholder_text(placeholder_text)

    def shell_cursor_position_changed(self, cursor_position):
        """ The change handler for the 'cursor_position' attribute on
        the shell.

        """
        if not self.setting_value:
            self.set_cursor_position(cursor_position)

    def shell_value_changed(self, value):
        """ The change handler for the 'text' attribute on the shell.

        """
        if not self.setting_value:
            self.update_text()
            self.shell_obj._modified = False

    def shell_converter_changed(self, converter):
        """ Handles the converter object on the shell changing.

        """
        self.update_text()
        event = wx.PyCommandEvent(wx.EVT_TEXT.typeId, self.widget.GetId())
        self.on_text_updated(event)

    def shell_password_mode_changed(self, mode):
        """ The change handler for the 'password_mode' attribute on the shell object.
        """
        shell = self.shell_obj
        self.set_password_mode(shell.password_mode)

    def set_selection(self, start, end):
        """ Sets the selection in the widget between the start and
        end positions, inclusive.

        """
        self.widget.SetSelection(start, end)
        self.update_shell_selection()

    def select_all(self):
        """ Select all the text in the line edit.

        If there is no text in the line edit, the selection will be
        empty.

        """
        self.widget.SetSelection(-1, -1)
        self.update_shell_selection()

    def deselect(self):
        """ Deselect any selected text.

        Sets a selection with start == stop to deselect the current
        selection. The cursor is placed at the beginning of selection.

        """
        widget = self.widget
        start, end = widget.GetSelection()
        widget.SetSelection(start, start)
        self.update_shell_selection()

    def clear(self):
        """ Clear the line edit of all text.

        """
        self.widget.Clear()
        self.update_shell_selection()

    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left
        of the cursor. Otherwise, it deletes the selected text.

        """
        widget = self.widget
        start, end = widget.GetSelection()
        if start == end:
            start = end - 1
        widget.Remove(start, end)
        self.update_shell_selection()

    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right
        of the cursor. Otherwise, it deletes the selected text.

        """
        widget = self.widget
        start, end = widget.GetSelection()
        if start == end:
            end = end + 1
        widget.Remove(start, end)
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
            start = widget.GetInsertionPoint()
            end = widget.GetLastPosition()
            widget.SetSelection(start, end)
        else:
            widget.SetInsertionPointEnd()
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
            end = widget.GetInsertionPoint()
            widget.SetSelection(start, end)
        else:
            widget.SetInsertionPoint(0)
        self.update_shell_selection()

    def cut(self):
        """ Cuts the selected text from the line edit.

        Copies the selected text to the clipboard then deletes the selected
        text from the line edit.

        """
        self.widget.Cut()
        self.update_shell_selection()

    def copy(self):
        """ Copies the selected text to the clipboard.

        """
        self.widget.Copy()
        self.update_shell_selection()

    def paste(self):
        """ Paste the contents of the clipboard into the line edit.

        Inserts the contents of the clipboard into the line edit at
        the current cursor position, replacing any selected text.

        """
        self.widget.Paste()
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
        self.widget.WriteText(text)
        self.update_shell_selection()

    def undo(self):
        """ Undoes the last operation.

        """
        self.widget.Undo()
        self.update_shell_selection()

    def redo(self):
        """ Redoes the last operation

        """
        self.widget.Redo()
        self.update_shell_selection()

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------


    def on_text_updated(self, event):
        """ The event handler for the text update event.

        """
        event.Skip()
        widget = self.widget
        shell = self.shell_obj
        text = widget.GetValue()
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

    def on_text_enter(self, event):
        """ The event handler for the return pressed event.

        """
        self.shell_obj.return_pressed = True

    def on_max_length(self, event):
        """ The event handler for the max length event.

        """
        self.shell_obj.max_length_reached = True

    def on_selection(self, event):
        """ The event handler for a selection (really a left up) event.

        """
        self.update_shell_selection()
        event.Skip()

    def update_shell_selection(self):
        """ Updates the selection and cursor position of the shell
        to reflect the current state of the widget.

        """
        shell = self.shell_obj
        widget = self.widget
        shell._selected_text = widget.GetStringSelection()
        self.setting_value = True
        shell.cursor_position = widget.GetInsertionPoint()
        self.setting_value = False

    def update_text(self):
        """ Updates the text control with the coverted shell value or
        sets the error state on the shell if the conversion fails.

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
            # wx.TextCtrl doesn't seem to accept input unless it has focus.
            self.widget.SetFocus()
            self.change_text(text)

    def change_text(self, text):
        """ Changes the text in the widget without emitted a text
        updated event. This should be called when the text is changed
        programmatically.

        """
        self.widget.ChangeValue(text)

    def set_max_length(self, max_length):
        """ Sets the max length of the widget to max_length.

        """
        self.widget.SetMaxLength(max_length)

    def set_read_only(self, read_only):
        """ Sets read only state of the widget.

        """
        # XXX this may require some trickery in Windows to change
        # this value properly on the fly.
        self.widget.SetEditable(not read_only)

    def set_placeholder_text(self, placeholder_text):
        self.widget.SetPlaceHolderText(placeholder_text)

    def set_cursor_position(self, cursor_position):
        """ Sets the cursor position of the widget.

        """
        self.widget.SetInsertionPoint(cursor_position)

    def set_password_mode(self, password_mode):
        """ Reflect the password_mode on the widget

        Currently WXField only supports `password` and normal`.

        """
        widget = self.widget
        if password_mode == 'normal':
            style = widget.GetWindowStyle()
            style &= ~wx.TE_PASSWORD
            style = widget.SetWindowStyle(style)
        elif password_mode == 'password':
            widget.SetWindowStyleFlag(wx.TE_PASSWORD)
        else:
            msg = ("The `silent` mode for the password_mode attribute is not"
                   " supported in WXField")
            warnings.warn(msg)

