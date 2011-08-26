import wx

from traits.api import implements, Bool, Event, Str

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

    #---------------------------------------------------------------------------
    # IPushButton interface
    #---------------------------------------------------------------------------
    down = Bool

    text = Str
    
    clicked = Event
    
    pressed = Event

    released = Event
    
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def create_widget(self, parent):
        widget = wx.Button(parent.widget)
        widget.Bind(wx.EVT_BUTTON, self._on_clicked)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        self.widget = widget

    def init_attributes(self):
        self.widget.SetLabel(self.text)

    def init_meta_handlers(self):
        pass

    def _text_changed(self, text):
        self.widget.SetLabel(text)
    
    def _on_clicked(self, event):
        self.down = False
        self.released = event
        self.clicked = event
        event.Skip()

    def _on_pressed(self, event):
        self.down = True
        self.pressed = event
        event.Skip()

    def _on_leave_window(self, event):
        # The wx button doesn't emit an EVT_LEFT_UP even though it 
        # emits an EVT_LEFT_DOWN (ugh!) So in order to reset the down 
        # flag when the mouse leaves the button and then releases, 
        # we need to hook the window leave event. (double ugh!)
        if self.down:
            self.down = False
            self.released = event
        event.Skip()

