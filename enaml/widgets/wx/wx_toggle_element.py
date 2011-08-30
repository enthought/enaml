from traits.api import implements, Bool, Str, Event

from .wx_element import WXElement

from ..i_toggle_element import IToggleElement


class WXToggleElement(WXElement):
    """ A base class for wxPython toggle widgets.

    This class can serve as a base class for widgets that implement
    toggle behavior such as CheckBox and RadioButton. It is not meant
    to be used directly. Subclasses should implement the 'create_widget'
    method.

    See Also
    --------
    IToggleElement

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
        """ Initializes the attributes of the underlying control.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        self.set_label(self.text)
        self.set_checked(self.checked)

    def init_meta_handlers(self):
        """ Initializes the meta handlers for the underlying control.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _checked_changed(self, checked):
        """ The change handler for the 'checked' attribute. Not meant
        for public consumption.

        """
        self.set_checked(checked)

    def _text_changed(self, text):
        """ The change handler for the 'text' attribute. Not meant
        for public consumption.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Event handlers
    #---------------------------------------------------------------------------
    def _on_toggled(self, event):
        """ The event handler for the toggled event. Not meant for
        public consumption.

        """
        self.down = False
        self.checked = self.widget.GetValue()
        self.released = True
        self.toggled = True
        event.Skip()

    def _on_pressed(self, event):
        """ The event handler for the pressed event. Not meant for
        public consumption.

        """
        self.down = True
        self.pressed = True
        event.Skip()

    def _on_leave_window(self, event):
        """ The event handler for the leave window event. Not meant for
        public consumption.

        """
        # The wx buttons don't emit an EVT_LEFT_UP even though they
        # emits an EVT_LEFT_DOWN (ugh!) So in order to reset the down 
        # flag when the mouse leaves the button and then releases, 
        # we need to hook the EVT_LEAVE_WINDOW
        if self.down:
            self.down = False
            self.released = True
        event.Skip()

    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_label(self, label):
        """ Sets the widget's label with the provided value. Not 
        meant for public consumption.

        """
        self.widget.SetLabel(label)

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.
        Not meant for public consumption.

        """
        self.widget.SetValue(checked)

