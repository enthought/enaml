from traits.api import HasTraits, Int, Tuple, Enum

from ..constants import Color


class Style(HasTraits):
    """Styles for an element."""

    # An element's background color.
    bg_color = Tuple(Color.DEFAULT)

    # The width of an element's border (px): top, right, bottom, left.
    border_size = Tuple(Int, Int, Int, Int)

    # The style of border lines.
    border_type = Enum('solid', 'dashed')
    
    # The color of an element's border.
    border_color = Tuple(Color.DEFAULT)
