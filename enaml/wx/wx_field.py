#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import re

import wx

from enaml.client_validation import make_validator

from .wx_constraints_widget import WxConstraintsWidget


class wxLineEdit(wx.TextCtrl):
    """ A wx.TextCtrl subclass which is similar to a QLineEdit in terms
    of features and behavior.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxLineEdit.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to initialize a
            wx.TextCtrl.

        """
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
    def GetBestSize(self):
        """ Overridden best size method to add 44 pixels in width to the
        field. This makes Wx consistent with Qt.

        """
        size = super(wxLineEdit, self).GetBestSize()
        return wx.Size(size.GetWidth() + 44, size.GetHeight())

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


class WxField(WxConstraintsWidget):
    """ A Wx implementation of an Enaml Field.

    """
    #: The validator to use for the field.
    _validator = None

    #: The edit triggers to use for the field.
    _edit_triggers = []

    #: The last edit value that was sent to/from the server
    _last_edit_text = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying wxLineEdit.

        """
        # We have to do a bit of initialization in the create method
        # since wx requires the style of certain things to be set at
        # the point of instantiation
        style = wx.TE_PROCESS_ENTER
        if tree['read_only']:
            style |= wx.TE_READONLY
        else:
            style &= ~wx.TE_READONLY
        echo_mode = tree['echo_mode']
        if echo_mode == 'normal':
            style &= ~wx.TE_PASSWORD
        else:
            style |= wx.TE_PASSWORD
        read_only = tree['read_only']
        if read_only:
            style |= wx.TE_READONLY
        else:
            style &= ~wx.TE_READONLY
        return wxLineEdit(parent, style=style)

    def create(self, tree):
        """ Create and initialize the wx field control.

        """
        super(WxField, self).create(tree)
        self.set_text(tree['text'])
        self.set_validator(tree['validator'])
        self.set_edit_triggers(tree['edit_triggers'])
        self.set_placeholder(tree['placeholder'])
        self.set_max_length(tree['max_length'])
        widget = self.widget
        widget.Bind(wx.EVT_KILL_FOCUS, self.on_lost_focus)
        widget.Bind(wx.EVT_TEXT_ENTER, self.on_return_pressed)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _send_edit_event(self):
        text = self.widget.GetValue()
        if text != self._last_edit_text:
            valid = True
            validator = self._validator
            if validator is not None:
                valid = validator(text)
            content = {'text': text, 'valid': valid}
            self.send_action('text_edited', content)
            self._last_edit_text = text

    #--------------------------------------------------------------------------
    # Event Handling
    #--------------------------------------------------------------------------
    def on_lost_focus(self, event):
        """ The event handler for the EVT_KILL_FOCUS event.

        """
        if 'lost_focus' in self._edit_triggers:
            self._send_edit_event()

    def on_return_pressed(self, event):
        """ The event handler for the EVT_TEXT_ENTER event.

        """
        if 'return_pressed' in self._edit_triggers:
            self._send_edit_event()

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        self.set_text(content['text'])

    def on_action_set_validator(self, content):
        """ Handle the 'set_validator' action from the Enaml widget.

        """
        self.set_validator(content['validator'])

    def on_action_set_edit_triggers(self, content):
        """ Handle the 'set_edit_triggers' action from the Enaml widget.

        """
        self.set_edit_triggers(content['edit_triggers'])

    def on_action_set_placeholder(self, content):
        """ Hanlde the 'set_placeholder' action from the Enaml widget.

        """
        self.set_placeholder(content['placeholder'])

    def on_action_set_echo_mode(self, content):
        """ Handle the 'set_echo_mode' action from the Enaml widget.

        """
        self.set_echo_mode(content['echo_mode'])

    def on_action_set_max_length(self, content):
        """ Handle the 'set_max_length' action from the Enaml widget.

        """
        self.set_max_length(content['max_length'])

    def on_action_set_read_only(self, content):
        """ Handle the 'set_read_only' action from the Enaml widget.

        """
        self.set_read_only(content['read_only'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Updates the text control with the given unicode text.

        """
        self.widget.ChangeValue(text)
        self._last_edit_text = text

    def set_validator(self, validator):
        """ Sets the validator for the control.

        """
        if validator is not None:
            validator = make_validator(validator)
        self._validator = validator
    
    def set_edit_triggers(self, triggers):
        """ Set the edit triggers for the control.

        """
        self._edit_triggers = triggers

    def set_placeholder(self, placeholder):
        """ Sets the placeholder text in the widget.

        """
        self.widget.SetPlaceHolderText(placeholder)

    def set_echo_mode(self, echo_mode):
        """ Sets the echo mode of the wiget.
        """
        # Wx cannot change the echo mode dynamically. It requires
        # creating a brand-new control, so we just ignore the change.
        pass

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
        # Wx cannot change the read only state dynamically. It requires
        # creating a brand-new control, so we just ignore the change.
        pass

