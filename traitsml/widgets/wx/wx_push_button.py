import wx

from traits.api import implements, Bool, Event, Str

from .wx_element import WXElement

from ..i_push_button import IPushButton


class WXPushButton(WXElement):
    """ A wxPython implementation of IPushButton.

    WXPushButton uses a wx.Button control.

    See Also
    --------
    IPushButton

    """
    implements(IPushButton)

    #===========================================================================
    # IPushButton interface
    #===========================================================================
    down = Bool

    text = Str

    clicked = Event

    pressed = Event

    released = Event

    #===========================================================================
    # Implementation
    #===========================================================================
    def create_widget(self):
        """ Creates the underlying wx.Button control.

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        widget = wx.Button(self.parent_widget())
        widget.Bind(wx.EVT_BUTTON, self._on_clicked)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        self.widget = widget

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def init_attributes(self):
        """ Intializes the widget with the attributes of this instance.

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        self.set_label(self.text)

    def init_meta_handlers(self):
        """ Initializes any meta handlers for this widget.

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _text_changed(self, text):
        """ The change handler for the 'text' attribute. Not meant for
        public consumption.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    def _on_clicked(self, event):
        """ The event handler for the button's clicked event. Not meant
        for public consumption.

        """
        self.down = False
        self.released = event
        self.clicked = event
        event.Skip()

    def _on_pressed(self, event):
        """ The event handlers for the button's pressed event. Not meant
        for public consumption.

        """
        self.down = True
        self.pressed = event
        event.Skip()

    def _on_leave_window(self, event):
        """ The event handler for the button's leave window event. Not
        meant for public consumption.

        """
        # The wxButton doesn't emit an EVT_LEFT_UP even though it 
        # emits an EVT_LEFT_DOWN (ugh!) So in order to reset the down 
        # flag when the mouse leaves the button and then releases,
        # we need to hook the EVT_LEAVE_WINDOW 
        if self.down:
            self.down = False
            self.released = event
        event.Skip()

    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_label(self, label):
        """ Sets the label on the button control. Not meant for public
        consumption.

        """
        self.widget.SetLabel(label)

