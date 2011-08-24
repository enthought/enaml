from traits.api import implements, Bool, Event, Str

import wx

from .wx_element import WXElement

from ..i_push_button import IPushButton


class WXPushButton(WXElement):
    """ A wxWidgets implementation of IPushButton.

    Attributes
    ----------
    down : Bool
        Whether or not the button is currently pressed.

    text : Str
        The text to use as the button's label.

    clicked : Event
        Fired when the button is clicked.

    pressed : Event
        Fired when the button is pressed.

    released: Event
        Fired when the button is released.

    See Also
    --------
    IPushButton
    """
    implements(IPushButton)

    # IPushButton interface
    down = Bool

    text = Str
    
    clicked = Event
    
    pressed = Event

    released = Event
    
    # Setup
    def init_widget(self, parent=None):
        """ NOTE: This method is a placeholder.

        It's a generic setup function, whose name might change in the future.
        Connecting the event handlers is necessary, but it might happen somewhere else.

        For now, it's okay to use.
        """
        
        self.widget.Bind(wx.EVT_BUTTON, self._on_clicked)
        self.widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        self.widget.Bind(wx.EVT_LEFT_UP, self._on_released)

    # Notification methods
    def _down_changed(self):
        self.widget.SetValue(self.down)
    
    def _text_changed(self):
        self.widget.SetLabel(self.text)
    
    # Event handlers
    def _on_clicked(self, event):
        self.clicked = event
        event.Skip()

    def _on_pressed(self, event):
        self.down = True
        self.pressed = event
        event.Skip()

    def _on_released(self, event):
        self.down = False
        self.released = event
        event.Skip()

