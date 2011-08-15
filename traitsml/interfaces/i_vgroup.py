from traits.api import ReadOnly

from .i_group import IGroup

from ..enums import Direction


class IVGroup(IGroup):
    """ A vertically grouping container.

    This is a convienence subclass of IGroup which hard codes
    the layout direction to Direction.TOP_TO_BOTTOM

    Attributes
    ----------
    direction : ReadOnly
    	The layout direction is hard coded to Direction.TOP_TO_BOTTOM
    
    """	
    direction = ReadOnly(Direction.TOP_TO_BOTTOM)

