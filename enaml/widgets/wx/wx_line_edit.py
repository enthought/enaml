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

        self.widget.ChangeValue(self.text)
        self.cursor_position = self.widget.GetInsertionPoint()
        self.text_changed = self.text


    def _read_only_changed(self):
        # only update if the value has actually changed
        if self.read_only == self.widget.IsEditable():
            self.widget.SetEditable(not self.read_only)

    def _max_length_changed(self):
        self.widget.SetMaxLength(self.max_length)

    def _cursor_position_changed(self):
        self.widget.SetInsertionPoint(self.cursor_position)

    #--------------------------------------------------------------------------
    # Event handlers
    #--------------------------------------------------------------------------

    def _on_max_length(self, event):
        # TODO: do something to show that no more characters are allowed
        event.skip()

    def _on_text_updated(self, event):
        new_text = self.widget.GetValue()
        if self.text != new_text:
            self.modified = True
            self.text = new_text
            self.text_edited = new_text
        event.Skip()

    def _on_text_enter(self, event):
        self.return_pressed = event
        event.Skip()

    def default_sizer_flags(self):
        return super(WXLineEdit, self).default_sizer_flags().Proportion(1)
