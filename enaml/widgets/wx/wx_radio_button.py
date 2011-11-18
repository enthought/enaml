#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_toggle_control import WXToggleControl

from ..radio_button import AbstractTkRadioButton


#: A new radio button event for the custom radio button this is emitted 
#: on the parent whenever any CustomRadioButton is toggled.
wxGroupRadio, EVT_GROUP_RADIO = wx.lib.newevent.NewEvent()

#: A radio button event emitted when the value is interactively turned on.
wxRadioToggleOn, EVT_RADIO_TOGGLE_ON = wx.lib.newevent.NewEvent()

#: A radio button event that is emited when the button is auto unchecked.
wxRadioToggleOff, EVT_RADIO_TOGGLE_OFF = wx.lib.newevent.NewEvent()

#: A radio button event emitted when the value is programatically turned on.
wxRadioSetChecked, EVT_RADIO_SET_CHECKED = wx.lib.newevent.NewEvent()

#: A radio button event emitted when the value is programatically turned off.
wxRadioSetUnchecked, EVT_RADIO_SET_UNCHECKED = wx.lib.newevent.NewEvent()


class CustomRadioButton(wx.RadioButton):
    """ A custom stubclass of wx.RadioButton.

    The wx.RadioButton doesn't emit toggled events when it unchecks
    the other radio buttons in the same group. So, the only time an
    EVT_RADIOBUTTON is emitted is when the button changes from off
    to on. This custom subclass does some orchestration and will
    emit an EVT_RADIOBUTTON_UNCHECKED event when the control cycles
    from on to off.

    """
    def __init__(self, *args, **kwargs):
        super(CustomRadioButton, self).__init__(*args, **kwargs)
        # This class works by binding every instance to an event that
        # is emitted on the parent. When an instance is toggled, it
        # emits the group event on the parent, which allows every other
        # instance with the same parent to check to see if it has been
        # unchecked. If it has, then it emits the unchecked event.
        self.Bind(wx.EVT_RADIOBUTTON, self.OnToggled)
        self.GetParent().Bind(EVT_GROUP_RADIO, self.OnGroupToggled)
        self._last = self.GetValue()

    def OnGroupToggled(self, event):
        """ Handles the event emmitted when one of the radio buttons from
        our group is toggled. Determines whether the button should emit
        a toggle off event.

        """
        last = self._last
        curr = self.GetValue()
        if not curr and last:
            self._last = curr
            off_evt = wxRadioToggleOff()
            wx.PostEvent(self, off_evt)
        event.Skip()

    def OnToggled(self, event):
        """ Handles the standard toggle event and emits a toggle on
        event.

        """
        self._last = self.GetValue()
        on_evt = wxRadioToggleOn()
        wx.PostEvent(self, on_evt)
        group_evt = wxGroupRadio()
        wx.PostEvent(self.GetParent(), group_evt)

    def SetValue(self, val):
        """ Overrides the default SetValue method to emit proper events.

        """
        old = self.GetValue()
        if old != val:
            super(CustomRadioButton, self).SetValue(val)
            self._last = val
            if not val:
                off_evt = wxRadioSetUnchecked()
                wx.PostEvent(self, off_evt)
            else:
                on_evt = wxRadioSetChecked()
                wx.PostEvent(self, on_evt)
            group_evt = wxGroupRadio()
            wx.PostEvent(self.GetParent(), group_evt)


class WXRadioButton(WXToggleControl, AbstractTkRadioButton):
    """ A wxPython implementation of RadioButton.

    WXRadioButton uses a custom wx.RadioButton control. Radio buttons
    with the same parent will be mutually exclusive. For independent
    groups, place them in their own parent compoenent.

    """
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying custom wx.RadioButton control.

        """
        self.widget = CustomRadioButton(self.parent_widget())

    def bind(self):
        """ Binds the event handlers of the control.

        """
        widget = self.widget
        widget.Bind(EVT_RADIO_TOGGLE_ON, self.on_toggled)
        widget.Bind(EVT_RADIO_TOGGLE_OFF, self.on_simple_toggle)
        widget.Bind(EVT_RADIO_SET_CHECKED, self.on_simple_toggle)
        widget.Bind(EVT_RADIO_SET_UNCHECKED, self.on_simple_toggle)
        widget.Bind(wx.EVT_LEFT_DOWN, self.on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self.on_released)

    def on_simple_toggle(self, event):
        """ An event handler for toggle events that have nothing to do
        with mouse interaction by the user and therefore the events
        emited by _on_toggled would be inappropriate.

        """
        shell = self.shell_obj
        shell.checked = self.widget.GetValue()
        shell.toggled = True
        event.Skip()

