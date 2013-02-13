#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WxControl


# Create event for a delayed text changed
wxEVT_TEXT_CHANGED = wx.NewEventType()
EVT_TEXT_CHANGED = wx.PyEventBinder(wxEVT_TEXT_CHANGED, 1)


class wxMultiLineEdit(wx.TextCtrl):
    """ A wx.TextCtrl subclass which is similar to a QMultiLineEdit in terms
    of features and behavior.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxMultiLineEdit.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to initialize a
            wx.TextCtrl.

        """
        super(wxMultiLineEdit, self).__init__(*args, **kwargs)
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimerFired, self._timer)
        self.Bind(wx.EVT_TEXT, self.OnTextEdited)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnTextEdited(self, event):
        """ Start the collapsing timer when the text is edited

        """
        self._timer.Start(200, oneShot=True)
        event.Skip()

    def OnTimerFired(self, event):
        """ Handles the wx.EVT_TIMER event for delayed text change event

        """
        textEvent = wx.CommandEvent(wxEVT_TEXT_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(textEvent)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetBestSize(self):
        """ Overridden best size method to add 246 pixels in width and 176
        pixels to the height. This makes Wx consistent with Qt.

        """
        size = super(wxMultiLineEdit, self).GetBestSize()
        return wx.Size(size.GetWidth() + 246, size.GetHeight() + 176)

    def ChangeValue(self, text):
        """ Overridden method which moves the insertion point to the end
        of the field when changing the text value. This causes the field
        to behave like Qt.

        """
        super(wxMultiLineEdit, self).ChangeValue(text)
        self.SetInsertionPoint(len(text))


class WxMultiLineEdit(WxControl):
    """ A Wx implementation of an Enaml Field.

    """
    #: The list of submit triggers for when to submit a text change.
    _submit_triggers = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying wxLineEdit.

        """
        # We have to do a bit of initialization in the create method
        # since wx requires the style of certain things to be set at
        # the point of instantiation
        style = wx.TE_MULTILINE
        if tree['read_only']:
            style |= wx.TE_READONLY
        else:
            style &= ~wx.TE_READONLY
        return wxMultiLineEdit(parent, style=style)

    def create(self, tree):
        """ Create and initialize the wx field control.

        """
        super(WxMultiLineEdit, self).create(tree)
        self.set_text(tree['text'])
        self.set_submit_triggers(tree['submit_triggers'])
        widget = self.widget()
        widget.Bind(wx.EVT_KILL_FOCUS, self.on_lost_focus)
        widget.Bind(EVT_TEXT_CHANGED, self.on_text_changed)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _submit_text(self):
        """ Submit the given text as an update to the server widget.

        Parameters
        ----------
        text : unicode
            The unicode text to send to the server widget.

        """
        text = self.widget().GetValue()
        content = {'text': text}
        self.send_action('submit_text', content)

    #--------------------------------------------------------------------------
    # Event Handling
    #--------------------------------------------------------------------------
    def on_lost_focus(self, event):
        """ The event handler for EVT_KILL_FOCUS event.

        """
        event.Skip()
        if 'lost_focus' in self._submit_triggers:
            self._submit_text()

    def on_text_changed(self, event):
        """ The event handler for EVT_TEXT_CHANGED event.

        """
        event.Skip()
        if 'text_changed' in self._submit_triggers:
            self._submit_text()

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        self.set_text(content['text'])

    def on_action_set_submit_triggers(self, content):
        """ Handle the 'set_submit_triggers' action from the Enaml
        widget.

        """
        self.set_submit_triggers(content['sumbit_triggers'])

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
        with self.loopback_guard('text'):
            self.widget().ChangeValue(text)

    def set_submit_triggers(self, triggers):
        """ Set the submit triggers for the underlying widget.

        """
        self._submit_triggers = triggers

    def set_read_only(self, read_only):
        """ Sets the read only state of the widget.

        """
        # Wx cannot change the read only state dynamically. It requires
        # creating a brand-new control, so we just ignore the change.
        pass

