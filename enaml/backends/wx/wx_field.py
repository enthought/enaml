#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from unicodedata import category as ucategory

import wx

from .wx_control import WXControl

from ...components.field import AbstractTkField
from ...guard import guard


class WXFieldValidator(wx.PyValidator):
    """ A wx.PyValidator implementation which proxies the work to the 
    Enaml validator installed on the shell component.

    """
    def __init__(self, validator):
        """ Initialize a WXFieldValidator

        Parameters
        ----------
        validator : AbstractValidator
            An instance of the Enaml AbstractValidator.

        """
        super(WXFieldValidator, self).__init__()
        self.validator = validator
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def Clone(self):
        """ A required wx.PyValidator method which returns a clone of
        this object by calling the constructor with the internal
        Enaml validator instance.

        """
        return self.__class__(self.validator)

    def OnChar(self, event):
        """ An event handler which intercepts the char events before the
        control is updated and runs the new string through the validator.

        """
        # We only need to validate the string if the key pressed can
        # actually have an effect on the displayable text. The following
        # clause simply filters any control keys which generate char
        # events, such as the arrow keys.
        uchar = unichr(event.GetUnicodeKey())
        if ucategory(uchar).startswith('C'):
            event.Skip()
            return

        # We only skip the char event if the new text validates as 
        # INTERMEDIATE or ACCEPTABLE. Otherwise, we kill the event
        # so that the control is not visibly updated.
        v = self.validator
        window = self.GetWindow()
        current = window.GetValue()
        idx = window.GetInsertionPoint()
        new = current[:idx] + uchar + current[idx:]
        if v.validate(new) != v.INVALID:
            event.Skip()

    def OnTextEnter(self, event):
        """ An event handler which intercepts the enter pressed event
        and only skips it if the text is valid or can be made valid.

        """
        v = self.validator
        window = self.GetWindow()
        current = window.GetValue()
        if v.validate(current) == v.ACCEPTABLE:
            event.Skip()
        else:
            new = v.normalize(current)
            if v.validate(new) == v.ACCEPTABLE:
                window.ChangeValue(new)
                event.Skip()
    
    def OnKillFocus(self, event):
        """ An event handler which intercepts the lost focus event
        and will attempt to make the text valid before forwarding 
        the event.

        """
        v = self.validator
        window = self.GetWindow()
        current = window.GetValue()
        if v.validate(current) != v.ACCEPTABLE:
            new = v.normalize(current)
            if v.validate(new) == v.ACCEPTABLE:
                window.ChangeValue(new)
        event.Skip()


class wxLineEdit(wx.TextCtrl):
    """ A wx.TextCtrl subclass which is similar to a QLineEdit in terms
    of features and validation behavior.

    """
    def __init__(self, *args, **kwargs):
        super(wxLineEdit, self).__init__(*args, **kwargs)
        self._placeholder_text = ''
        self._placeholder_active = False
        self._user_fgcolor = None
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _UpdatePlaceholderDisplay(self):
        """ Updates the display with the placeholder text if no text
        is currently set for the control.
        
        """ 
        if not self.GetValue() and self._placeholder_text:
            self.ChangeValue(self._placeholder_text)
            color = wx.Color(95, 95, 95)
            super(wxLineEdit, self).SetForegroundColour(color)
            self._placeholder_active = True

    def _RemovePlaceholderDisplay(self):
        """ Removes the placeholder text if it is currently active.

        """
        if self._placeholder_active:
            self.ChangeValue('')
            color = self._user_fgcolor or wx.Color(0, 0, 0)
            super(wxLineEdit, self).SetForegroundColour(color)
            self._placeholder_active = False

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnKillFocus(self, event):
        """ Refreshes the placeholder display when the control loses
        focus.

        """
        self._UpdatePlaceholderDisplay()
        event.Skip()

    def OnSetFocus(self, event):
        """ Removes the placeholder display when the control receives
        focus.

        """
        self._RemovePlaceholderDisplay()
        event.Skip()
    
    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def SetPlaceHolderText(self, placeholder_text):
        """ Sets the placeholder text to the given value. Pass an empty
        string to turn off the placeholder text functionality.

        """
        self._placeholder_text = placeholder_text
        self._UpdatePlaceholderDisplay()

    def GetPlaceHolderText(self):
        """ Returns the placeholder text for this control.

        """
        return self._placeholder_text

    def ChangeValue(self, text):
        """ Overridden method which moves the insertion point to the end
        of the field when changing the text value. This causes the field
        to behave like Qt.

        """
        super(wxLineEdit, self).ChangeValue(text)
        self.SetInsertionPoint(len(text))

    def GetValue(self):
        """ Returns string value in the control, or an empty string if
        the placeholder text is active.

        """
        if self._placeholder_active:
            return ''
        return super(wxLineEdit, self).GetValue()

    def SetForegroundColour(self, wxColor, force=False):
        """ Sets the foreground color of the field. If the placeholder
        text is being shown, `force` must be True in order to override
        the placeholder text color.

        """
        self._user_fgcolor = wxColor
        if self._placeholder_active and not force:
            return
        super(wxLineEdit, self).SetForegroundColour(wxColor)

    def Clone(self, parent, style=None):
        """ Clone the wxLineEdit widget.

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
        new_widget = self.__class__(parent=parent, style=style)
        new_widget._placeholder_text = self._placeholder_text
        new_widget._placeholder_active = self._placeholder_active
        new_widget.SetForegroundColour(self._user_fgcolor)
        new_widget.ChangeValue(self.GetValue())
        new_widget.SetInsertionPoint(self.GetInsertionPoint())
        new_widget.SetSelection(*self.GetSelection())
        # We have to clone the validator or WX will segfault when we
        # set it on the new widget.
        validator = self.GetValidator().Clone()
        if validator is not None:
            new_widget.SetValidator(validator)
        return new_widget


class WXField(WXControl, AbstractTkField):
    """ A wxPython implementation of a LineEdit.

    The LineEdit uses a custom wx.TextCtrl and provides a single line of
    editable text.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wxLineEdit.

        """
        # We have to do a bit of initialization in the create method
        # since wx requires the style of certain things to be set at
        # the point of instantiation
        style = wx.TE_PROCESS_ENTER
        shell = self.shell_obj

        if shell.read_only:
            style |= wx.TE_READONLY
        else:
            style &= ~wx.TE_READONLY
        
        password_mode = shell.password_mode
        if password_mode == 'normal':
            style &= ~wx.TE_PASSWORD
        elif password_mode == 'password':
            style |= wx.TE_PASSWORD
        else:
            style |= wx.TE_PASSWORD

        self.widget = wxLineEdit(parent=parent, style=style)

    def initialize(self):
        """ Initializes the attributes of the wxLineEdit.

        """
        super(WXField, self).initialize()
        shell = self.shell_obj
        self.set_validator(shell.validator)
        self.set_text(shell.validator.format(shell.value))
        self.set_placeholder_text(shell.placeholder_text)
        self.set_cursor_position(shell.cursor_position)
        self.set_max_length(shell.max_length)

    def bind(self):
        """ Binds the event handlers for the wx.TextCtrl.

        """
        super(WXField, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_TEXT, self.on_text_edited)
        widget.Bind(wx.EVT_TEXT_ENTER, self.on_return_pressed)
        widget.Bind(wx.EVT_KILL_FOCUS, self.on_lost_focus)
        widget.Bind(wx.EVT_LEFT_UP, self.on_selection_changed)

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
        shell.

        """
        self.set_max_length(max_length)

    def shell_read_only_changed(self, read_only):
        """ The change handler for the 'read_only' attribute on the
        shell.

        """
        self.set_read_only(read_only)

    def shell_cursor_position_changed(self, cursor_position):
        """ The change handler for the 'cursor_position' attribute on
        the shell.

        """
        if not guard.guarded(self, 'updating_selection'):
            self.set_cursor_position(cursor_position)

    def shell_placeholder_text_changed(self, placeholder_text):
        """ The change handler for the 'placeholder_text' attribute on
        the shell.

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
        """ Sets the selection in the widget between the start and
        end positions, inclusive.

        """
        self.widget.SetSelection(start, end)
        self._update_shell_selection_and_cursor()

    def select_all(self):
        """ Select all the text in the line edit.

        If there is no text in the line edit, the selection will be
        empty.

        """
        self.widget.SetSelection(-1, -1)
        self._update_shell_selection_and_cursor()

    def deselect(self):
        """ Deselect any selected text.

        Sets a selection with start == stop to deselect the current
        selection. The cursor is placed at the beginning of selection.

        """
        widget = self.widget
        start, end = widget.GetSelection()
        widget.SetSelection(start, start)
        self._update_shell_selection_and_cursor()

    def clear(self):
        """ Clear the line edit of all text.

        """
        self.widget.Clear()
        self._update_shell_selection_and_cursor()

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
        self._update_shell_selection_and_cursor()

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
        self._update_shell_selection_and_cursor()

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
        self._update_shell_selection_and_cursor()

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
        self._update_shell_selection_and_cursor()

    def cut(self):
        """ Cuts the selected text from the line edit.

        Copies the selected text to the clipboard then deletes the selected
        text from the line edit.

        """
        self.widget.Cut()
        self._update_shell_selection_and_cursor()

    def copy(self): 
        """ Copies the selected text to the clipboard.

        """
        self.widget.Copy()
        self._update_shell_selection_and_cursor()

    def paste(self):
        """ Paste the contents of the clipboard into the line edit.

        Inserts the contents of the clipboard into the line edit at
        the current cursor position, replacing any selected text.

        """
        self.widget.Paste()
        self._update_shell_selection_and_cursor()

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
        self._update_shell_selection_and_cursor()

    def undo(self):
        """ Undoes the last operation.

        """
        self.widget.Undo()
        self._update_shell_selection_and_cursor()

    def redo(self):
        """ Redoes the last operation

        """
        self.widget.Redo()
        self._update_shell_selection_and_cursor()
    
    #--------------------------------------------------------------------------
    # Event handlers
    #--------------------------------------------------------------------------
    def on_text_edited(self, event):
        """ The event handler for when the user edits the text through 
        the ui.

        """
        event.Skip()
        self.shell_obj._field_text_edited()

    def on_return_pressed(self, event):
        """ The event handler for the return pressed event.

        """
        # Don't skip the event here or it will result in an annoying
        # Windows system beep.
        self.shell_obj._field_return_pressed()

    def on_lost_focus(self, event):
        """ The signal handler for the lost focus event.

        """
        event.Skip()
        self.shell_obj._field_lost_focus()

    def on_selection_changed(self, event):
        """ The event handler for a selection event.

        """
        event.Skip()
        self._update_shell_selection_and_cursor()

    #--------------------------------------------------------------------------
    # Updated Methods
    #--------------------------------------------------------------------------
    def get_text(self):
        """ Returns the current unicode text in the control.

        """
        return self.widget.GetValue()
    
    def set_text(self, text):
        """ Updates the text control with the given unicode text.

        """
        self.widget.ChangeValue(text)

    def set_validator(self, validator):
        """ Wraps the given Enaml validator in a custom wx.PyValidator 
        instance and applies it to the underlying control.

        """
        wxvalidator = WXFieldValidator(validator)
        self.widget.SetValidator(wxvalidator)
    
    def set_max_length(self, max_length):
        """ Set the max length of the control to max_length. If the max 
        length is <= 0 or > 32767 then the control will be set to hold 
        32kb of text.

        """
        if (max_length <= 0) or (max_length > 32767):
            max_length = 32767
        self.widget.SetMaxLength(max_length)

    def set_read_only(self, read_only):
        """ Sets the read only state of the widget. 

        """
        # Since the read-only state can only be set at creation time,
        # we need to create a new widget and swap it out. This is a
        # terrible hack that is forced upon us by wx limitations.
        style = self.widget.GetWindowStyle()
        if read_only:
            style |= wx.TE_READONLY
        else:
            style &= ~wx.TE_READONLY
        style |= wx.TE_PROCESS_ENTER
        self._update_widget_style(style)

    def set_placeholder_text(self, placeholder_text):
        """ Sets the placeholder text in the widget.

        """
        self.widget.SetPlaceHolderText(placeholder_text)

    def set_cursor_position(self, cursor_position):
        """ Sets the cursor position of the widget.

        """
        self.widget.SetInsertionPoint(cursor_position)

    def set_password_mode(self, password_mode):
        """ Sets the password mode of the wiget. Currently WXField only
        supports `password` and normal`.

        """
        # Since the read-only state can only be set at creation time,
        # we need to create a new widget and swap it out. This is a
        # terrible hack that is forced upon us by wx limitations.
        widget = self.widget
        style = widget.GetWindowStyle()
        if password_mode == 'normal':
            style &= ~wx.TE_PASSWORD
        elif password_mode == 'password':
            style |= wx.TE_PASSWORD
        else:
            style |= wx.TE_PASSWORD
        style |= wx.TE_PROCESS_ENTER
        self._update_widget_style(style)

    #--------------------------------------------------------------------------
    # Helper Methods
    #--------------------------------------------------------------------------
    def _update_shell_selection_and_cursor(self):
        """ Update the selection and cursor position for the shell
        object.

        """
        # This isn't nearly as nice as Qt. We can only update the 
        # selection due to a left up event because wx doesn't provide
        # any better/more relevant events. This means this function 
        # is just call whenver any change in the control *may* have
        # caused these things to update. We are doing way more work
        # here that we should be needing to, but the only way around
        # this that I see is to implement our own control from scratch.
        with guard(self, 'updating_selection'):
            self.shell_obj.selected_text = self.widget.GetStringSelection()
            self.shell_obj.cursor_position = self.widget.GetInsertionPoint()

    def _update_widget_style(self, style):
        """ Create a new CustomTextWidget widget with the given style
        and use it as the new widget, destroying the old one.

        """
        widget = self.widget
        new_widget = widget.Clone(parent=widget.GetParent(), style=style)
        widget.Destroy()
        self.widget = new_widget
        self.bind()
        new_widget.Show()
        # We need a relayout to put the new widget in the proper position.
        self.shell_obj.request_relayout()
    
    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def size_hint(self):
        """ Overridden size_hint method to add 44 pixels in width to 
        the field. This makes Wx consistent with Qt.

        """
        w, h = super(WXField, self).size_hint()
        return (w + 44, h)

