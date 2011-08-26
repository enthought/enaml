from traits.api import implements, Bool, Event, Str

import wx

from .wx_element import WXElement

from ..i_check_box import ICheckBox


class WXCheckBox(WXElement):
    """A wxWidgets implementation of ICheckBox.

    Attributes
    ----------
    checked : Bool
        Whether or not the button is currently checked.

    text : Str
         The text to show next to the check box.

    toggled : Event
        Fired when the check box is toggled.

    pressed : Event
        Fired when the check box is pressed.

    released : Event
        Fired when the check box is released.

    """
    implements(ICheckBox)

    #--------------------------------------------------------------------------
    # IRadioButton interface
    #--------------------------------------------------------------------------

    checked = Bool

    text = Str

    toggled = Event

    pressed = Event

    released = Event

    #--------------------------------------------------------------------------
    #
    # Implementation
    #
    #--------------------------------------------------------------------------

    def create_widget(self, parent=None):
        """Initialization of ICheckBox element based on wxWidget
        """
        # create widget
        widget = wx.CheckBox(parent=parent.widget)

        # Bind class functions to wxwidget events
        widget.Bind(wx.EVT_CHECKBOX, self._on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEFT_UP, self._on_released)

        # associate widget
        self.widget = widget

    #--------------------------------------------------------------------------
    # Initialization methods
    #--------------------------------------------------------------------------

    def init_attributes(self):
        """initialize wxCheckBox attributes"""
        self.widget.SetLabel(self.text)
        self.widget.SetValue(self.checked)

    def init_meta_handlers(self):
        """initialize wxCheckBox meta styles"""
        pass

    #--------------------------------------------------------------------------
    # Notification methods
    #--------------------------------------------------------------------------

    def _checked_changed(self):
        # only update if the value has actually changed
        if self.checked != self.widget.GetValue():
            self.widget.SetValue(self.checked)
            self.toggled = True

    def _text_changed(self):
        self.widget.SetLabel(self.text)

    #--------------------------------------------------------------------------
    # Event handlers
    #--------------------------------------------------------------------------

    def _on_toggled(self, event):
        self.checked = not self.checked
        self.toggled = event
        event.Skip()

    def _on_pressed(self, event):
        self.pressed = event
        event.Skip()

    def _on_released(self, event):
        self.released = event
        event.Skip()
