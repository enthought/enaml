import wx

from traits.api import implements

from .wx_toggle_element import WXToggleElement

from ..i_radio_button import IRadioButton


class WXRadioButton(WXToggleElement):
    """ A wxPython implementation of IRadioButton.

    .. note:: When wxRadioButtons are in the same group (but not inside a
        radiobox) selecting one of them will automatically deselect the 
        others. Yet the other WXRadioButtons will not be aware of the 
        change even though the wxWidgets have changed their values.

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
        """ Creates and binds a wx.RadioButton.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        widget = wx.RadioButton(self.parent_widget())
        widget.Bind(wx.EVT_RADIOBUTTON, self._on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        self.widget = widget

