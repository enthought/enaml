import wx

from traits.api import implements

from ..i_element import IElement

from .wx_component import WXComponent


class WXElement(WXComponent):

    implements(IElement)

    #===========================================================================
    # IElement interface
    #===========================================================================
    def layout(self, parent):
        self.set_parent(parent)
        self.create_widget()
        self.init_attributes()
        self.init_meta_handlers()

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        raise NotImplementedError
        
    def init_attributes(self):
        raise NotImplementedError

    def init_meta_handlers(self):
        raise NotImplementedError
    
    #---------------------------------------------------------------------------
    # Layout helpers
    #---------------------------------------------------------------------------
    def default_sizer_flags(self):
        """ The default sizing for an element is aligned top-left
        with a 2 pixel border, a proportion of 0 and expanding.

        """
        return wx.SizerFlags(0).Left().Top().Border(wx.ALL, 2).Expand()

