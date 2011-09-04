import wx

from traits.api import implements

from .wx_group import WXGroup

from ..hgroup import IHGroupImpl


class WXHGroup(WXGroup):
    """ A wxPython implementation of IHGroup.

    This is a convienence subclass of WXGroup which restrict the
    layout to horizontal.

    See Also
    --------
    IHGroup
    
    """ 
    implements(IHGroupImpl)

    #---------------------------------------------------------------------------
    # IHGroupImpl interface
    #---------------------------------------------------------------------------
    
    # IHGroupImpl interface is empty and implemented by WXGroup
    
    # We don't *necessarily* need to override this method since 
    # the direction will always be horizontal, but this will speed
    # things up just a hair.
    def make_sizer(self, direction):
        return wx.BoxSizer(wx.HORIZONTAL)

