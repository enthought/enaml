import wx

from traits.api import implements

from .wx_toggle_control import WXToggleControl

from ..check_box import ICheckBoxImpl


class WXCheckBox(WXToggleControl):
    """ A wxPython implementation of ICheckBox.

    A Checkbox provides a toggleable control using a wx.CheckBox.

    See Also
    --------
    ICheckBox

    """
    implements(ICheckBoxImpl)

    #---------------------------------------------------------------------------
    # ICheckBoxImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates and binds a wx.CheckBox.

        """
        self.widget = wx.CheckBox(self.parent_widget())
        
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        widget = self.widget
        widget.Bind(wx.EVT_CHECKBOX, self._on_toggled)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)  

