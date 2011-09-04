import wx

from traits.api import implements

from .wx_component import WXComponent

from ..panel import IPanelImpl


class WXPanel(WXComponent):
    """ A wxPython implementation of IPanel.

    A panel aranges it children onto a wx.Panel.

    See Also
    --------
    IPanel

    """
    implements(IPanelImpl)

    #---------------------------------------------------------------------------
    # IPanelImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wxPanel.

        """
        self.widget = wx.Panel(self.parent_widget())
    
    def initialize_widget(self):
        """ There is nothing to initialize on a panel.

        """
        pass
    
    def layout_child_widgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for child in self.child_widgets():
            sizer.Add(child, 1, wx.EXPAND)
        self.widget.SetSizer(sizer)
        sizer.Layout()
