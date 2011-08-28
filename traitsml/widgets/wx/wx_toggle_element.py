from traits.api import implements, Bool, Str, Event

from .wx_element import WXElement

from ..i_toggle_element import IToggleElement


class WXToggleElement(WXElement):
    """ A base class for wxPython toggle widgets.

    This class can serve as a base class for widgets that implement
    toggle behavior such as CheckBox and RadioButton. It is not meant
    to be used directly. Subclasses should implement the 'create_widget'
    widget.

    Attributes
    ----------
    checked : Bool
        Whether or not the element is currently checked. This is has
        bi-directional behavior in that programmatically setting the 
        value will cause the element to be updated. However, if
        setting the value programatically, a toggled event *will not*
        be emitted.

    down : Bool
        Whether the user is currently pressing the check box.
        
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

    .. note:: The wx toggle elements don't reliably emit EVT_LEFT_UP
    events even thought they emit EVT_LEFT_DOWN. This results in
    suboptimal behavior because we don't know if the mouse has been
    released if the user releases the mouse when not over the control.
    As a workaround, we hook the EVT_LEAVE_WINDOW which is not ideal,
    but probably the best we can do in wx.

    """
    implements(IToggleElement)

    #===========================================================================
    # IToggleElement interface
    #===========================================================================
    checked = Bool

    down = Bool
    
    text = Str

    toggled = Event

    pressed = Event

    released = Event

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Intitialization
    #---------------------------------------------------------------------------
    def init_attributes(self):
        self.set_label(self.text)
        self.set_checked(self.checked)

    def init_meta_handlers(self):
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _checked_changed(self, checked):
        """ The change handler for the 'checked' attribute.

        """
        self.set_checked(checked)

    def _text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Event handlers
    #---------------------------------------------------------------------------
    def _on_toggled(self, event):
        """ The event handler for the toggled event.

        """
        self.down = False
        self.checked = self.widget.GetValue()
        self.released = event
        self.toggled = event
        event.Skip()

    def _on_pressed(self, event):
        """ The event handler for the pressed event.

        """
        self.down = True
        self.pressed = event
        event.Skip()

    def _on_leave_window(self, event):
        """ The event handler for the leave window event.

        """
        # The wx buttons don't emit an EVT_LEFT_UP even though they
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
        """ Update the widget's label with the provided value.

        """
        self.widget.SetLabel(label)

    def set_checked(self, checked):
        """ Update the widget's checked state with the provided value.

        """
        self.widget.SetValue(checked)

