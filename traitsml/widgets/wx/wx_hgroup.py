from traits.api import Enum, implements

from .wx_group import WXGroup

from ..i_hgroup import IHGroup

from ...enums import Direction


class WXHGroup(WXGroup):
    """ A wxPython implementation of IHGroup

    This is a convienence subclass of WXGroup which restrict the
    layout to horizontal.

    See Also
    --------
    IHGroup
    
    """ 
    implements(IHGroup)

    #===========================================================================
    # IHGroup interface
    #===========================================================================
    direction = Enum(Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT)

