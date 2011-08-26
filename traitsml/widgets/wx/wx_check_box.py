from traits.api import implements, Bool, Event, Str

import wx

from .wx_element import WXElement

from ..i_check_box import ICheckBox


class WXCheckBox(WXElement):
    """A wxPython implementation of ICheckBox.

    Attributes
    ----------
    checked : Bool
        Whether or not the button is currently checked. This is has
        bi-directional behavior in that programmatically setting the 
        value will cause the check box to be updated. However, if
        setting the value programatically, a toggled event *will not*
        be emitted.

    text : Str
         The text to show next to the check box.

    toggled : Event
        Fired when the check box is toggled. This event is only triggered
        in response to user interaction with the widget.

    pressed : Event
        Fired when the check box is pressed. This event is only triggered
        in response to user interaction with the widget.

    released : Event
        Fired when the check box is released.

    .. note:: The wx.CheckBox doesn't emit an wx.EVT_LEFT_UP even though it 
        emits a wx.EVT_LEFT_DOWN. So in order to reset the down flag when 
        the mouse leaves the button and then releases, we need hook to 
        wx.EVT_LEAVE_WINDOW event. This results in slighly suboptimal
        behavior if pressing down on a button, the dragging away before
        releasing. But it seems to be the best we can do in wx.

    See Also
    --------
    ICheckBox

    """
    implements(ICheckBox)

    #===========================================================================
    # ICheckBox interface
    #===========================================================================
    down = Bool

    checked = Bool

    text = Str

    toggled = Event

    pressed = Event

    released = Event
    
    #===========================================================================
    # Implementation
    #===========================================================================
    def create_widget(self, parent):
        """ Creates and binds a wx.CheckBox.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Arguments
        ---------
        parent : WXContainer
            The WXContainer instance that is our parent

        Returns
        -------
        result : None

        """
        widget = wx.CheckBox(parent.widget)
        widget.Bind(wx.EVT_CHECKBOX, self._on_toggled)
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
        self.widget.SetLabel(self.text)
        self.widget.SetValue(self.checked)

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
    def _checked_changed(self, checked):
        """ The change handler for the 'checked' attribute.

        """
        self.widget.SetValue(self.checked)

    def _text_changed(self):
        """ The change handler for the 'text' attribute.

        """
        self.widget.SetLabel(self.text)
    
    #---------------------------------------------------------------------------
    # Event Handling
    #---------------------------------------------------------------------------
    def _on_toggled(self, event):
        """ The event handler for the button's toggled event.

        """
        self.down = False
        self.checked = self.widget.GetValue()
        self.released = event
        self.toggled = event
        event.Skip()

    def _on_pressed(self, event):
        """ The event handler for the button's pressed event.

        """
        self.down = True
        self.pressed = event
        event.Skip()

    def _on_leave_window(self, event):
        """ The event handler for the button's leave window event.

        """
        # The wx.CheckBox doesn't emit an EVT_LEFT_UP even though it 
        # emits an EVT_LEFT_DOWN (ugh!) So in order to reset the down 
        # flag when the mouse leaves the button and then releases, 
        # we need to hook the EVT_LEAVE_WINDOW
        if self.down:
            self.down = False
            self.released = event
        event.Skip()

