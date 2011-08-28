import wx
import wx.lib.newevent

from traits.api import implements

from .wx_toggle_element import WXToggleElement

from ..i_radio_button import IRadioButton


# A new radio button event for the custom radio button this is emitted on 
# the parent whenever any CustomRadioButton is toggled. This allows other
# radio buttons in the group to determine if they've been changed and
# then emit a toggled event.
wxGroupRadioButton, EVT_GROUP_RADIOBUTTON = wx.lib.newevent.NewEvent()


# A new radio button event that is emitted by a button when it is unchecked
# automatically by wx.
wxRadioButtonUnchecked, EVT_RADIOBUTTON_UNCHECKED = wx.lib.newevent.NewEvent()


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
        self.GetParent().Bind(EVT_GROUP_RADIOBUTTON, self.OnGroupToggled)
        self._last = self.GetValue()

    def OnGroupToggled(self, event):
        last = self._last
        if not self.GetValue() and last:
            self._last = False
            evt = wxRadioButtonUnchecked()
            wx.PostEvent(self, evt)
        event.Skip()

    def OnToggled(self, event):
        event.Skip()
        self._last = self.GetValue()
        evt = wxGroupRadioButton()
        wx.PostEvent(self.GetParent(), evt)


class WXRadioButton(WXToggleElement):
    """ A wxPython implementation of IRadioButton.

    WXRadioButton uses the wx.RadioButton control. Radio buttons with 
    the same parent will be mutually exclusive. For independent groups,
    place them in their own Panel.

    See Also
    --------
    IRadioButton

    """
    implements(IRadioButton)

    #===========================================================================
    # IRadioButton interface
    #===========================================================================
    
    # IRadioButton is an empty interface that inherits from IToggleElement

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wx.RadioButton control.

        This method is called by the 'layout' method and is not meant
        for public consumption.

        """
        widget = CustomRadioButton(self.parent_widget())
        widget.Bind(wx.EVT_RADIOBUTTON, self._on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        widget.Bind(EVT_RADIOBUTTON_UNCHECKED, self._on_unchecked)
        self.widget = widget

    #---------------------------------------------------------------------------
    # Event handlers
    #---------------------------------------------------------------------------
    def _on_unchecked(self, event):
        self.checked = self.widget.GetValue()
        self.toggled = True
        event.Skip()

