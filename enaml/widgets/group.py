from traits.api import Enum

from .container import Container

from ..enums import Direction


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

