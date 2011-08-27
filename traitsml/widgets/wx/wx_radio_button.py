# -*- coding: utf-8 -*-
import wx

from traits.api import implements, Bool, Event, Str

from .wx_element import WXElement
from ..i_radio_button import IRadioButton


class WXRadioButton(WXElement):
    """ A wxWidgets implementation of IRadioButton.

    Radio buttons are created

    Attributes
    ----------
    checked : Bool
        Whether the button is currently checked.

    text : Str
        The text to use as the button's label.

    toggled : Event
        Fired when the button is toggled.

    pressed : Event
        Fired when the button is pressed.

    released : Event
        Fired when the button is released.


    .. note:: When wxRadioButtons are in the same group (but not inside a
        radiobox) selecting one of them will automatically deselect the others.
        Yet the other WXRadioButtons will not be aware of the change even
        though the wxWidgets have changed their values.

    See Also
    --------
    IRadioButton
    wxRadioButton

    """
    implements(IRadioButton)

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

    def create_widget(self, parent):
        """Initialization of the IRadionButton based on wxWidget
        """
        # create widget
        widget = wx.RadioButton(parent=parent.widget)

        # Bind class functions to wx widget events
        widget.Bind(wx.EVT_RADIOBUTTON, self._on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEFT_UP, self._on_released)

        # associate widget
        self.widget = widget

    #--------------------------------------------------------------------------
    # Initialization methods
    #--------------------------------------------------------------------------

    def init_attributes(self):
        """initialize wxRadioButton attributes"""
        self.widget.SetLabel(self.text)
        self.widget.SetValue(self.checked)

    def init_meta_handlers(self):
        """initialize wxRadioButton meta styles"""
        pass

    #--------------------------------------------------------------------------
    # Notification methods
    #--------------------------------------------------------------------------

    def _checked_changed(self):
        # only update if the value has actually change
        if self.checked != self.widget.GetValue():
            self.widget.SetValue(self.checked)
            self.toggled = True

    def _text_changed(self):
        self.widget.SetLabel(self.text)

    #--------------------------------------------------------------------------
    # Event handlers
    #--------------------------------------------------------------------------

    def _on_toggled(self, event):
        self.checked = self.widget.GetValue()
        self.toggled = event
        event.Skip()

    def _on_pressed(self, event):
        self.pressed = event
        event.Skip()

    def _on_released(self, event):
        self.released = event
        event.Skip()
