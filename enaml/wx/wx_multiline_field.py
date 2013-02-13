#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_control import WxControl


#: The event used to signal a delayed text change.
wxTextChangedEvent, EVT_TEXT_CHANGED = wx.lib.newevent.NewEvent()


class wxMultilineField(wx.TextCtrl):
    """ A text control which notifies on a collpasing timer.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxMultilineField.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to initialize a
            wx.TextCtrl.

        """
        super(wxMultilineField, self).__init__(*args, **kwargs)
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimerFired, self._timer)
        self.Bind(wx.EVT_TEXT, self.OnTextEdited)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnTextEdited(self, event):
        """ Restart the collapsing timer when the text is edited.

        """
        self._timer.Start(200, oneShot=True)
        event.Skip()

    def OnTimerFired(self, event):
        """ Handles the wx.EVT_TIMER event for delayed text change.

        """
        event = wxTextChangedEvent()
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetBestSize(self):
        """ A reimplemented best size method.

        This adds 246 pixels in width and 176 pixels to the height to
        make Wx consistent with Qt.

        """
        size = super(wxMultilineField, self).GetBestSize()
        return wx.Size(size.GetWidth() + 246, size.GetHeight() + 176)

    def ChangeValue(self, text):
        """ An overridden parent class method.

        This moves the insertion point to the end of the field when the
        text value changes. This makes the field to behave like Qt.

        """
        super(wxMultilineField, self).ChangeValue(text)
        self.SetInsertionPointEnd()


class WxMultilineField(WxControl):
    """ A Wx implementation of an Enaml Field.

    """
    #: Whether or not to auto synchronize the text on change.
    _auto_sync_text = True

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying wxMultiLineField.

        """
        style = wx.TE_MULTILINE | wx.TE_RICH
        return wxMultilineField(parent, style=style)

    def create(self, tree):
        """ Create and initialize the wx field control.

        """
        super(WxMultilineField, self).create(tree)
        self._auto_sync_text = tree['auto_sync_text']
        self.set_text(tree['text'])
        self.set_read_only(tree['read_only'])
        widget = self.widget()
        widget.Bind(EVT_TEXT_CHANGED, self.on_text_changed)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _send_text_changed(self):
        """ Send the current text as an update to the server widget.

        """
        text = self.widget().GetValue()
        self.send_action('text_changed', {'text': text})

    #--------------------------------------------------------------------------
    # Event Handling
    #--------------------------------------------------------------------------
    def on_text_changed(self, event):
        """ The event handler for EVT_TEXT_CHANGED event.

        """
        if self._auto_sync_text and 'text' not in self.loopback_guard:
            self._send_text_changed()

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        self.set_text(content['text'])

    def on_action_set_auto_sync_text(self, content):
        """ Handle the 'set_auto_sync_text' action from the Enaml widget.

        """
        self._auto_sync_text = content['auto_sync_text']

    def on_action_set_read_only(self, content):
        """ Handle the 'set_read_only' action from the Enaml widget.

        """
        self.set_read_only(content['read_only'])

    def on_action_sync_text(self, content):
        """ Handle the 'sync_text' action from the Enaml widget.

        """
        self._send_text_changed()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Updates the text control with the given unicode text.

        """
        with self.loopback_guard('text'):
            self.widget().ChangeValue(text)

    def set_read_only(self, read_only):
        """ Sets the read only state of the widget.

        """
        self.widget().SetEditable(not read_only)

