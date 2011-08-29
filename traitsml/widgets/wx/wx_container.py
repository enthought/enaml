import wx

from traits.api import implements, Bool

from .wx_component import WXComponent

from ..i_container import IContainer
from ..mixins.container_mixin import ContainerMixin


class WXContainer(WXComponent, ContainerMixin):
    """ A wxPython implementation of IContainer.

    The WXContainer class serves as a base class for other container
    widgets. It is not meant to be used directly.

    See Also
    --------
    IContainer

    """
    implements(IContainer)

    #===========================================================================
    # IContainer interface
    #===========================================================================
    def layout(self, parent):
        """ Initialize and layout the the container and its children.

        This method will be called by the 'layout' method of the 
        container's parent. It is not meant for public consumption.

        """
        self.set_parent(parent)
        self.create_widget()
        self.layout_children()
        self.init_attributes()
        self.init_meta_handlers()
        self.layed_out = True

    # The rest of the IContainer interface is provided by the ContainerMixin

    #===========================================================================
    # Implementation
    #===========================================================================
    # A flag to tell whether or not we've been layed out proper
    # and we can therefore expect our children to have widgets
    layed_out = Bool(False)
    
    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget (or sizer) for the container.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        raise NotImplementedError

    def layout_children(self):
        """ Layout the children of the container.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        raise NotImplementedError

    def init_attributes(self):
        """ Initialize the attributes of the container.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        raise NotImplementedError

    def init_meta_handlers(self):
        """ Intialize the meta handlers for the container.

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    # Layout helpers
    #---------------------------------------------------------------------------
    def default_sizer_flags(self):
        """ Computes the default sizer flags based on the flags of its
        children. Names the flags will only be expanding if one of its
        children is exanding.

        """
        for child in self.children():
            flags = child.default_sizer_flags()
            if flags.GetFlags() & wx.EXPAND:
                expand = True
                break
        else:
            expand = False
        
        if expand:
            res = wx.SizerFlags().Expand().Border(wx.ALL, 5)
        else:
            res = wx.SizerFlags().Border(wx.ALL, 5)
        
        return res

