from traits.api import implements

from .wx_control import WXControl

from ..toggle_control import IToggleControlImpl


class WXToggleControl(WXControl):
    """ A base class for wxPython toggle widgets.

    This class can serve as a base class for widgets that implement
    toggle behavior such as CheckBox and RadioButton. It is not meant
    to be used directly. Subclasses should implement the 'create_widget'
    method.

    See Also
    --------
    IToggleElement

    """
    implements(IToggleControlImpl)

    #---------------------------------------------------------------------------
    # IToggleControlImpl interface
    #---------------------------------------------------------------------------
    def initialize_widget(self):
        """ Initializes the attributes of the underlying control.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        parent = self.parent
        self.set_label(parent.text)
        self.set_checked(parent.checked)
        self.bind()

    def parent_checked_changed(self, checked):
        """ The change handler for the 'checked' attribute. Not meant
        for public consumption.

        """
        self.set_checked(checked)

    def parent_text_changed(self, text):
        """ The change handler for the 'text' attribute. Not meant
        for public consumption.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # implementation
    #---------------------------------------------------------------------------
    def bind(self):
        raise NotImplementedError

    def _on_toggled(self, event):
        """ The event handler for the toggled event. Not meant for
        public consumption.

        """
        self.parent.down = False
        self.parent.checked = self.widget.GetValue()
        self.parent.released = True
        self.parent.toggled = True
        event.Skip()

    def _on_pressed(self, event):
        """ The event handler for the pressed event. Not meant for
        public consumption.

        """
        self.parent.down = True
        self.parent.pressed = True
        event.Skip()

    def _on_leave_window(self, event):
        """ The event handler for the leave window event. Not meant for
        public consumption.

        """
        # The wx buttons don't emit an EVT_LEFT_UP even though they
        # emits an EVT_LEFT_DOWN (ugh!) So in order to reset the down 
        # flag when the mouse leaves the button and then releases, 
        # we need to hook the EVT_LEAVE_WINDOW
        if self.parent.down:
            self.parent.down = False
            self.parent.released = True
        event.Skip()

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

