from traits.api import HasTraits, Int, List

from .color import Color
from .style_sheet import NO_STYLE


def color_from_color_style(color_style):
    """ Converts a color style value into a proper Color. Falling back
    to Color.no_color if it can't be converted.

    """
    if color_style is NO_STYLE:
        color = Color.no_color
    elif isinstance(color_style, basestring):
        color = Color.from_string(color_style.strip())
    elif isinstance(color_style, Color):
        color = color_style
    else:
        color = Color.no_color
    return color


class PaddingStyle(HasTraits):

    padding = List(Int, minlen=4, maxlen=4)

    @classmethod
    def from_style_node(cls, style_node):
        get_property = style_node.get_property
        padding = [-1, -1, -1, -1]
        
        style_padding = get_property("padding")
        if isinstance(style_padding, (tuple, list)):
            if all(isinstance(item, int) for item in style_padding):
                n = len(style_padding)
                if n == 0:
                    pass
                elif n == 1:
                    padding[:] = style_padding * 4
                elif n == 2:
                    padding[0] = padding[2] = style_padding[0]
                    padding[1] = padding[3] = style_padding[1]
                elif n == 3:
                    padding[:3] = style_padding
                    padding[3] = padding[1]
                elif n == 4:
                    padding[:] = style_padding
                else:
                    pass
        elif isinstance(style_padding, int):
            padding[:] = [style_padding] * 4
        else:
            pass
            
        padding_top = get_property("padding_top")
        if isinstance(padding_top, int):
            padding[0] = padding_top

        padding_right = get_property("padding_right")
        if isinstance(padding_right, int):
            padding[1] = padding_right
        
        padding_bottom = get_property("padding_bottom")
        if isinstance(padding_bottom, int):
            padding[2] = padding_bottom

        padding_left = get_property("padding_left")
        if isinstance(padding_left, int):
            padding[3] = padding_left

        return cls(padding=padding)

