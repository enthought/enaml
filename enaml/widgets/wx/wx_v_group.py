#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import implements

from .wx_group import WXGroup

from ..v_group import IVGroupImpl


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
    
    # IVGroupImpl interface is empty and fully implemented by WXGroup

