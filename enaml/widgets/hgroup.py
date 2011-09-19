#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Instance

from .group import Group, IGroupImpl

from ..enums import Direction


class IHGroupImpl(IGroupImpl):
    pass


class HGroup(Group):
    """ A horizontally grouping container.

    This is a convienence subclass of Group which restricts the 
    layout direction to horizontal.

    Attributes
    ----------
    direction : Enum(Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT)
    	The layout direction restricted to horizontal directions.
    
    """	
    direction = Enum(Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IHGroupImpl)

