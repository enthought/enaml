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

    def Clone(self, parent, style=None):
        """ Clone the CustomTextCtrl widget.

        Arguments
        ---------
        parent: wx.Window
            The parent to use for the new widget.

        style: int
            The style to use for the new widget. Default is to use the
            same style as the current object.

        """
        if style is None:
            style = self.GetWindowStyle()

        new_widget = CustomTextCtrl(parent=parent, style=style)
        new_widget._placeholder_text = self._placeholder_text
        new_widget._placeholder_active = self._placeholder_active
        new_widget.SetForegroundColour(self._user_fgcolor)
        new_widget.ChangeValue(self.GetValue())
        new_widget.SetInsertionPoint(self.GetInsertionPoint())
        new_widget.SetSelection(*self.GetSelection())
        new_widget.SetPosition(self.GetPosition())
        new_widget.SetSize(self.GetSize())
        new_widget.SetDoubleBuffered(True)
        return new_widget

class WXField(WXControl, AbstractTkField):
    """ A wxPython implementation of a LineEdit.

    The LineEdit uses a custom wx.TextCtrl and provides a single line of
    editable text.

   """
    #: A flag which set to True when we're applying updates to the
    #: model. Allows us to avoid unnecessary notification recursion.
    setting_value = False

    #--------------------------------------------------------------------------
    # Setup Methods
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
        self._set_max_length(shell.max_length)
        self._set_placeholder_text(shell.placeholder_text)
        if shell.value:
            self._update_text()
        shell._modified = False
        self._set_cursor_position(shell.cursor_position)

    def bind(self):
        """ Binds the event handlers for the wx.TextCtrl.

        """
        super(WXField, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_TEXT_MAXLEN, self._on_max_length)
        widget.Bind(wx.EVT_TEXT, self._on_text_updated)
        widget.Bind(wx.EVT_TEXT_ENTER, self._on_text_enter)
        widget.Bind(wx.EVT_LEFT_UP, self._on_selection)

    #--------------------------------------------------------------------------
    # Notifiers
    #--------------------------------------------------------------------------

    def shell_max_length_changed(self, max_length):
        """ The change handler for the 'max_length' attribute on the
        shell.

        """
        self._set_max_length(max_length)
        self.shell_obj.size_hint_updated = True

    def shell_read_only_changed(self, read_only):
        """ The change handler for the 'read_only' attribute on the
        shell.

        """
        self._set_read_only(read_only)

    def shell_placeholder_text_changed(self, placeholder_text):
        """ The change handler for the 'placeholder_text' attribute on
        the shell.

        """
        self._set_placeholder_text(placeholder_text)

    def shell_cursor_position_changed(self, cursor_position):
        """ The change handler for the 'cursor_position' attribute on
        the shell.

        """
        if not self.setting_value:
            self._set_cursor_position(cursor_position)

    def shell_value_changed(self, value):
        """ The change handler for the 'text' attribute on the shell.

        """
        if not self.setting_value:
            self._update_text()
            self.shell_obj._modified = False

    def shell_converter_changed(self, converter):
        """ Handles the converter object on the shell changing.

        """
        self._update_text()
        event = wx.PyCommandEvent(wx.EVT_TEXT.typeId, self.widget.GetId())
        self._on_text_updated(event)

    def shell_password_mode_changed(self, mode):
        """ The change handler for the 'password_mode' attribute on the
        shell object.

        """
        shell = self.shell_obj
        self._set_password_mode(shell.password_mode)

    #---------------------------------------------------------------------------
    # Event handlers
    #---------------------------------------------------------------------------

    def _on_text_enter(self, event):
        self.shell_obj.return_pressed = True

    def _on_max_length(self, event):
        self.shell_obj.max_length_reached = True

    def _on_selection(self, event):
        self._update_shell_selection()
        event.Skip()

    def _on_text_updated(self, event):
        """ The event handler for the text update event.

        """
        event.Skip()
        shell = self.shell_obj
        text = self.widget.GetValue()
        self.setting_value = True
        with shell.capture_notification_exceptions():
            value = shell.converter.from_component(text)
            shell.value = value
        self.setting_value = False
        self._update_shell_selection()
        shell._modified = True
        shell.text_changed = text

    #--------------------------------------------------------------------------
    # Public methods
    #--------------------------------------------------------------------------

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
        self._update_shell_selection()

    def select_all(self):
        """ Select all the text in the line edit.

        If there is no text in the line edit, the selection will be
        empty.

        """
        self.widget.SetSelection(-1, -1)
        self._update_shell_selection()

    def deselect(self):
        """ Deselect any selected text.

        Sets a selection with start == stop to deselect the current
        selection. The cursor is placed at the beginning of selection.

        """
        widget = self.widget
        start, end = widget.GetSelection()
        widget.SetSelection(start, start)
        self._update_shell_selection()

    def clear(self):
        """ Clear the line edit of all text.

        """
        self.widget.Clear()
        self._update_shell_selection()

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
        self._update_shell_selection()

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
        self._update_shell_selection()

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
        self._update_shell_selection()

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
        self._update_shell_selection()

    def cut(self):
        """ Cuts the selected text from the line edit.

        Copies the selected text to the clipboard then deletes the selected
        text from the line edit.

        """
        self.widget.Cut()
        self._update_shell_selection()

    def copy(self):
        """ Copies the selected text to the clipboard.

        """
        self.widget.Copy()
        self._update_shell_selection()

    def paste(self):
        """ Paste the contents of the clipboard into the line edit.

        Inserts the contents of the clipboard into the line edit at
        the current cursor position, replacing any selected text.

        """
        self.widget.Paste()
        self._update_shell_selection()

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
        self._update_shell_selection()

    def undo(self):
        """ Undoes the last operation.

        """
        self.widget.Undo()
        self._update_shell_selection()

    def redo(self):
        """ Redoes the last operation

        """
        self.widget.Redo()
        self._update_shell_selection()

    #---------------------------------------------------------------------------
    # Private methods
    #---------------------------------------------------------------------------

    def _set_max_length(self, max_length):
        self.widget.SetMaxLength(max_length)

    def _set_placeholder_text(self, placeholder_text):
        self.widget.SetPlaceHolderText(placeholder_text)

    def _set_cursor_position(self, cursor_position):
        self.widget.SetInsertionPoint(cursor_position)

    def _update_shell_selection(self):
        """ Updates the selection and cursor position of the shell
        to reflect the current state of the widget.

        """
        shell = self.shell_obj
        widget = self.widget
        shell._selected_text = widget.GetStringSelection()
        self.setting_value = True
        shell.cursor_position = widget.GetInsertionPoint()
        self.setting_value = False

    def _update_text(self):
        """ Updates the text control with the coverted shell value or
        sets the error state on the shell if the conversion fails.

        """
        shell = self.shell_obj
        with shell.capture_exceptions():
            text = shell.converter.to_component(shell.value)
            # wx.TextCtrl doesn't seem to accept input unless it has focus.
            self.widget.SetFocus()
            self._change_text(text)

    def _change_text(self, text):
        """ Changes the text in the widget without emitted a text
        updated event. This should be called when the text is changed
        programmatically.

        """
        self.widget.ChangeValue(text)

    def _set_read_only(self, read_only):
        """ Sets the read only state of the widget.

        Notes
        -----
        The widget is actually cloned with the correct style and replaced.

        """
        style = self.widget.GetWindowStyle()
        if read_only:
            style |= wx.TE_READONLY
        else:
            style &= ~wx.TE_READONLY
        new_widget = self._create_new_widget(style)
        self._replace_widget(new_widget)

    def _set_password_mode(self, password_mode):
        """ Reflect the password_mode on the widget

        Currently WXField only supports `password` and normal`.

        Notes
        -----
        The widget is actually cloned with the correct style and replaced.

        """
        widget = self.widget
        style = widget.GetWindowStyle()
        if password_mode == 'normal':
            style &= ~wx.TE_PASSWORD
        elif password_mode == 'password':
            style |= wx.TE_PASSWORD
        else:
            msg = ("The `silent` mode for the password_mode attribute is not"
                   " supported in WXField")
            warnings.warn(msg)
        new_widget = self._create_new_widget(style)
        self._replace_widget(new_widget)


    def _create_new_widget(self, style):
        """ Create a new CustomTextWidget widget with the given style.

        """
        new_widget = self.widget.Clone(parent=self.parent_widget(),
                                        style=style | wx.TE_PROCESS_ENTER)
        return new_widget

    def _replace_widget(self, new_widget):
        """ Replace the internal widget with a new one.

        First destory the old widget. Then assign the new widget to
        :attr:`widget` and rebind the callbacks to the events. Finally
        show the widget and ask for re-layout.

        """

        self.widget.Destroy()
        self.widget = new_widget
        self.bind()
        self.widget.Show()
        self.widget.Refresh()
        self.shell_obj.size_hint_updated = True

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

