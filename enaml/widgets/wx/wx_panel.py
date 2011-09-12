import wx

from traits.api import implements

from .wx_component import WXComponent

from ..panel import IPanelImpl

from ...enums import SizePolicy


class WXPanel(WXComponent):
    """ A wxPython implementation of Panel.

    A panel aranges it children onto a wx.Panel.

    See Also
    --------
    Panel

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
        """ Arrange the child widgets onto the panel. The children are
        all Container which provide their own layout. Typically, there
        will be only one container, but in case there are more, all 
        containers get added to a vertical box sizer.

        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        #for child in self.child_widgets():
        #    sizer.Add(child, 1, wx.EXPAND)
        for child in self.parent.children:
            size_policy = child.get_style('size_policy')
            stretch = child.get_style('stretch')
            spacing = child.get_style('spacing')
            if size_policy == SizePolicy.EXPANDING:
                flag = wx.EXPAND
            else:
                flag = 0
            sizer.Add(child.toolkit_impl.widget, stretch, flag | wx.ALL, spacing)
        self.widget.SetSizer(sizer)
        sizer.Layout()
