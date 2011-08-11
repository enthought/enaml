from traits.api import Bool, Interface, Int, Tuple, Enum

from ..constants import Align, Color


class IStyle(Interface):
    """ Styles for an element. """

    align = Enum(Align.DEFAULT, *Align.values())

    # An element's foreground color.
    fg_color = Tuple(Color.DEFAULT)

    # An element's background color.
    bg_color = Tuple(Color.DEFAULT)

    # The width of an element's border (px): top, right, bottom, left.
    border_size = Tuple(Int, Int, Int, Int)

    # The style of border lines.
    border_type = Enum('solid', 'dashed')
    
    # The color of an element's border.
    border_color = Tuple(Color.DEFAULT)

    # Whether or not to wrap text.
    wrap = Bool


