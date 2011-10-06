#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Instance

from .group import Group, IGroupImpl

from ..enums import Direction


class IVGroupImpl(IGroupImpl):
    pass


class VGroup(Group):
    """ A vertically grouping container.

    This is a convienence subclass of Group which restricts the
    layout direction to vertical.

    Attributes
    ----------
    direction : Enum(Direction.TOP_TO_BOTTOM, Direction.BOTTOM_TO_TOP)
    	The layout direction is restricted to vertical directions.
    
    """	
    direction = Enum(Direction.TOP_TO_BOTTOM, Direction.BOTTOM_TO_TOP)

    #---------------------------------------------------------------------------
    # Overridden parent traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IVGroupImpl)

