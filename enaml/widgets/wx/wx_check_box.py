import wx

from traits.api import implements

from .wx_toggle_element import WXToggleElement

from ..i_check_box import ICheckBox


class WXCheckBox(WXToggleElement):
    """ A wxPython implementation of ICheckBox.

    A Checkbox provides a toggleable control using a wx.CheckBox.

    See Also
    --------
    ICheckBox

    """
    implements(ICheckBox)

    #===========================================================================
    # ICheckBox interface
    #===========================================================================
    
    # ICheckBox is an empty interface that inherits from IToggleElement
    
    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates and binds a wx.CheckBox.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        """
        widget = wx.CheckBox(self.parent_widget())
        widget.Bind(wx.EVT_CHECKBOX, self._on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        self.widget = widget

