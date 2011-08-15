from traits.api import ReadOnly

from .i_group import IGroup

from ..enums import Direction


class IHGroup(IGroup):
    """ A horizontally grouping container.

    This is a convienence subclass of IGroup which hard codes
    the layout direction to Direction.LEFT_TO_RIGHT

    Attributes
    ----------
    direction : ReadOnly
    	The layout direction is hard coded to Direction.LEFT_TO_RIGHT
    
    """	
    direction = ReadOnly(Direction.LEFT_TO_RIGHT)

