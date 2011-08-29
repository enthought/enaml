from traits.api import Enum, implements

from .wx_group import WXGroup

from ..i_vgroup import IVGroup

from ...enums import Direction


class WXVGroup(WXGroup):
    """ A wxPython implementation of IVGroup.

    This is a convienence subclass of WXGroup which restricts the 
    layout direction to vertical.

    See Also
    --------
    IVGroup
    
    """ 
    implements(IVGroup)

    #===========================================================================
    # IHGroup interface
    #===========================================================================
    direction = Enum(Direction.TOP_TO_BOTTOM, Direction.BOTTOM_TO_TOP)

