import wx

from traits.api import implements, Bool, Event, Str

from .wx_element import WXElement

from ..i_push_button import IPushButton


class WXPushButton(WXElement):
    """ A wxPython implementation of IPushButton.

    Attributes
    ----------
    down : Bool
        Whether or not the button is currently pressed. This is single
        direction as a result of user interaction with the widget.  
        Programmatically changing this value will not cause the button 
        to become pressed.

    text : Str
        The text to use as the button's label.

    clicked : Event
        Fired when the button is clicked. This event is only triggered
        in response to user interaction with the widget.

    pressed : Event
        Fired when the button is pressed. This event is only triggered
        in response to user interaction with the widget.

    released: Event
        Fired when the button is released. This event is only triggered
        in response to user interaction with the widget.


    .. note:: The wx.Button doesn't emit an wx.EVT_LEFT_UP even though it 
        emits a wx.EVT_LEFT_DOWN. So in order to reset the down flag when 
        the mouse leaves the button and then releases, we need hook to 
        wx.EVT_LEAVE_WINDOW event. This results in slighly suboptimal
        behavior if pressing down on a button, the dragging away before
        releasing. But it seems to be the best we can do in wx.


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

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.set_label(self.text)

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

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    def _on_clicked(self, event):
        """ The event handler for the button's clicked event.

        """
        self.down = False
        self.released = event
        self.clicked = event
        event.Skip()

    def _on_pressed(self, event):
        """ The event handlers for the button's pressed event.

        """
        self.down = True
        self.pressed = event
        event.Skip()

    def _on_leave_window(self, event):
        """ The event handler for the button's leave window event.

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
        self.widget.SetLabel(label)

