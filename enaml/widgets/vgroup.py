from traits.api import Enum

from .group import Group

from ..enums import Direction


class VGroup(Group):
    """ A vertically grouping container.

    This is a convienence subclass of IGroup which restricts the
    layout direction to vertical.

    Attributes
    ----------
    direction : Enum(Direction.TOP_TO_BOTTOM, Direction.BOTTOM_TO_TOP)
    	The layout direction is restricted to vertical directions.
    
    """	
    direction = Enum(Direction.TOP_TO_BOTTOM, Direction.BOTTOM_TO_TOP)

