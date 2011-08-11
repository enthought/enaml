from traits.api import Bool, Interface, Int, Tuple, Enum

from ..constants import Align, Border, Color


class IStyle(Interface):
    """ Styles for an element.

    Attributes
    ----------
    align : Enum
        An element's alignment, specified as a constant.

    fg_color = Tuple
        An element's foreground color, given as an RGBA value.

    bg_color : Tuple
        An element's background color, given as an RGBA value.

    border_size = Tuple
        The width of an element's border (px): top, right, bottom, left.

    border_type = Enum
        The style of border lines, specified as a constant.

    border_color = Tuple
        The color of an element's border.

    wrap = Bool
        Whether or not to wrap text.

    """
    align = Enum(Align.DEFAULT, *Align.values())

    fg_color = Tuple(Color.DEFAULT)

    bg_color = Tuple(Color.DEFAULT)

    border_size = Tuple(Int, Int, Int, Int)

    border_type = Enum(Border.DEFAULT, *Border.values())
    
    border_color = Tuple(Color.DEFAULT)

    wrap = Bool


