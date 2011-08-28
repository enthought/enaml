import wx

from traits.api import implements

from .wx_toggle_element import WXToggleElement

from ..i_radio_button import IRadioButton


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
        widget = wx.RadioButton(self.parent_widget())
        widget.Bind(wx.EVT_RADIOBUTTON, self._on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        self.widget = widget

