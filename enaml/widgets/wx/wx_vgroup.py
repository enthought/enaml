import wx

from traits.api import implements

from .wx_group import WXGroup

from ..vgroup import IVGroupImpl


class WXVGroup(WXGroup):
    """ A wxPython implementation of IVGroup.

    This is a convienence subclass of WXGroup which restricts the 
    layout direction to vertical.

    See Also
    --------
    IVGroup
    
    """ 
    implements(IVGroupImpl)

    #---------------------------------------------------------------------------
    # IVGroupImpl interface
    #---------------------------------------------------------------------------
    
    # IVGroupImpl interface is empty and implemented by WXGroup

    # We don't *necessarily* need to override this method since 
    # the direction will always be horizontal, but this will speed
    # things up just a hair.
    def make_sizer(self, direction):
        return wx.BoxSizer(wx.VERTICAL)

