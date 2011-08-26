import wx

from traits.api import implements, Bool, Event, Str

from .wx_element import WXElement

from ..i_push_button import IPushButton


class WXPushButton(WXElement):
    """ A wxPython implementation of IPushButton.

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


    .. note:: The wxbutton doesn't emit an wx.EVT_LEFT_UP even though it emits
        an wx.EVT_LEFT_DOWN. So in order to reset the down flag when the mouse
        leaves the button and then releases, we hook to wx.EVT_LEAVE_WINDOW
        event.


    See Also
    --------
    IPushButton

    """
    implements(IPushButton)

    #--------------------------------------------------------------------------
    # IPushButton interface
    #--------------------------------------------------------------------------
    down = Bool

    text = Str

    clicked = Event

    pressed = Event

    released = Event

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def create_widget(self, parent):
        """ Creates and binds a wx.Button.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Arguments
        ---------
        parent : WXContainer
            The WXContainer instance that is our parent.

        Returns
        -------
        result : None

        """
        widget = wx.Button(parent.widget)
        widget.Bind(wx.EVT_BUTTON, self._on_clicked)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        self.widget = widget

    def init_attributes(self):
        """ Intializes the widget with the attributes of this instance.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.widget.SetLabel(self.text)

    def init_meta_handlers(self):
        """ Initializes any meta handlers for this widget.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        pass

    def _text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.widget.SetLabel(text)

    def _on_clicked(self, event):
        """ The event handler for the buttons clicked event.

        """
        self.down = False
        self.released = event
        self.clicked = event
        event.Skip()

    def _on_pressed(self, event):
        """ The event handlers for the buttons pressed event.

        """
        self.down = True
        self.pressed = event
        event.Skip()

    def _on_leave_window(self, event):
        """ The event handler for the buttons leave window event.

        """
        # The wxButton doesn't emit an EVT_LEFT_UP even though it 
        # emits an EVT_LEFT_DOWN (ugh!) So in order to reset the down 
        # flag when the mouse leaves the button and then releases, 
        if self.down:
            self.down = False
            self.released = event
        event.Skip()
