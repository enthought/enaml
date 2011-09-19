#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Instance

from .container import Container, IContainerImpl

from ..enums import Direction


class IGroupImpl(IContainerImpl):
    
    def parent_direction_changed(self, direction):
        raise NotImplementedError


class Group(Container):
    """ A grouping container.
    
    A container that lays out it's children according to the value
    of 'direction'.

    Attributes
    ----------
    direction : Direction Enum value
        The direction in which to layout the children. The default
        is Direction.LEFT_TO_RIGHT.
        
    """
    direction = Enum(*Direction.values())  

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IGroupImpl)

