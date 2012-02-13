#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from traits.api import implements

from .wx_component import WXComponent
from .styling import compute_sizer_flags

from ..panel import IPanelImpl


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
        
    def create_style_handler(self):
        """ Creates and sets the window style handler.

        """
        pass
    
    def initialize_style(self):
        """ Initializes the style for the window.

        """
        pass
        
    def layout_child_widgets(self):
        """ Arrange the child widgets onto the panel. The children are
        all Container which provide their own layout. Typically, there
        will be only one container, but in case there are more, all 
        containers get added to a vertical box sizer.

        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        for child in self.parent.children:
            flags = compute_sizer_flags(child)
            sizer.AddF(child.toolkit_impl.widget, flags)
        self.widget.SetSizer(sizer)
        sizer.Layout()

