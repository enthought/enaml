#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A utility module for dealing with colors.

"""
from colorsys import hls_to_rgb
import re


#: Regex sub-expressions used for building more complex expression.
_int = r'\s*((?:\+|\-)?[0-9]+)\s*'
_intp = r'\s*((?:\+|\-)?[0-9]+)%\s*'
_real = r'\s*((?:\+|\-)?[0-9]*(?:\.[0-9]+)?)\s*'

#: Regular expressions used by the parsing routines.
_HEX_RE = re.compile(r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$', re.UNICODE)
_RGB_NUM_RE = re.compile(r'^rgb\(%s,%s,%s\)$' % (_int, _int, _int), re.UNICODE)
_RGB_PER_RE = re.compile(r'^rgb\(%s,%s,%s\)$' % (_intp, _intp, _intp), re.UNICODE)
_RGBA_NUM_RE = re.compile(r'^rgba\(%s,%s,%s,%s\)$' % (_int, _int, _int, _real), re.UNICODE)
_RGBA_PER_RE = re.compile(r'^rgba\(%s,%s,%s,%s\)$' % (_intp, _intp, _intp, _real), re.UNICODE)
_HSL_RE = re.compile(r'^hsl\(%s,%s,%s\)$' % (_int, _intp, _intp), re.UNICODE)
_HSLA_RE = re.compile(r'^hsla\(%s,%s,%s,%s\)$' % (_int, _intp, _intp, _real), re.UNICODE)


#: A table of all 147 named CSS colors.
_COLOR_TABLE = {
    'aliceblue': (240, 248, 255, 1.0),
    'antiquewhite': (250, 235, 215, 1.0),
    'aqua': (0, 255, 255, 1.0),
    'aquamarine': (127, 255, 212, 1.0),
    'azure': (240, 255, 255, 1.0),
    'beige': (245, 245, 220, 1.0),
    'bisque': (255, 228, 196, 1.0),
    'black': (0, 0, 0, 1.0),
    'blanchedalmond': (255, 235, 205, 1.0),
    'blue': (0, 0, 255, 1.0),
    'blueviolet': (138, 43, 226, 1.0),
    'brown': (165, 42, 42, 1.0),
    'burlywood': (222, 184, 135, 1.0),
    'cadetblue': (95, 158, 160, 1.0),
    'chartreuse': (127, 255, 0, 1.0),
    'chocolate': (210, 105, 30, 1.0),
    'coral': (255, 127, 80, 1.0),
    'cornflowerblue': (100, 149, 237, 1.0),
    'cornsilk': (255, 248, 220, 1.0),
    'crimson': (220, 20, 60, 1.0),
    'cyan': (0, 255, 255, 1.0),
    'darkblue': (0, 0, 139, 1.0),
    'darkcyan': (0, 139, 139, 1.0),
    'darkgoldenrod': (184, 134, 11, 1.0),
    'darkgray': (169, 169, 169, 1.0),
    'darkgreen': (0, 100, 0, 1.0),
    'darkgrey': (169, 169, 169, 1.0),
    'darkkhaki': (189, 183, 107, 1.0),
    'darkmagenta': (139, 0, 139, 1.0),
    'darkolivegreen': (85, 107, 47, 1.0),
    'darkorange': (255, 140, 0, 1.0),
    'darkorchid': (153, 50, 204, 1.0),
    'darkred': (139, 0, 0, 1.0),
    'darksalmon': (233, 150, 122, 1.0),
    'darkseagreen': (143, 188, 143, 1.0),
    'darkslateblue': (72, 61, 139, 1.0),
    'darkslategray': (47, 79, 79, 1.0),
    'darkslategrey': (47, 79, 79, 1.0),
    'darkturquoise': (0, 206, 209, 1.0),
    'darkviolet': (148, 0, 211, 1.0),
    'deeppink': (255, 20, 147, 1.0),
    'deepskyblue': (0, 191, 255, 1.0),
    'dimgray': (105, 105, 105, 1.0),
    'dimgrey': (105, 105, 105, 1.0),
    'dodgerblue': (30, 144, 255, 1.0),
    'firebrick': (178, 34, 34, 1.0),
    'floralwhite': (255, 250, 240, 1.0),
    'forestgreen': (34, 139, 34, 1.0),
    'fuchsia': (255, 0, 255, 1.0),
    'gainsboro': (220, 220, 220, 1.0),
    'ghostwhite': (248, 248, 255, 1.0),
    'gold': (255, 215, 0, 1.0),
    'goldenrod': (218, 165, 32, 1.0),
    'gray': (128, 128, 128, 1.0),
    'grey': (128, 128, 128, 1.0),
    'green': (0, 128, 0, 1.0),
    'greenyellow': (173, 255, 47, 1.0),
    'honeydew': (240, 255, 240, 1.0),
    'hotpink': (255, 105, 180, 1.0),
    'indianred': (205, 92, 92, 1.0),
    'indigo': (75, 0, 130, 1.0),
    'ivory': (255, 255, 240, 1.0),
    'khaki': (240, 230, 140, 1.0),
    'lavender': (230, 230, 250, 1.0),
    'lavenderblush': (255, 240, 245, 1.0),
    'lawngreen': (124, 252, 0, 1.0),
    'lemonchiffon': (255, 250, 205, 1.0),
    'lightblue': (173, 216, 230, 1.0),
    'lightcoral': (240, 128, 128, 1.0),
    'lightcyan': (224, 255, 255, 1.0),
    'lightgoldenrodyellow': (250, 250, 210, 1.0),
    'lightgray': (211, 211, 211, 1.0),
    'lightgreen': (144, 238, 144, 1.0),
    'lightgrey': (211, 211, 211, 1.0),
    'lightpink': (255, 182, 193, 1.0),
    'lightsalmon': (255, 160, 122, 1.0),
    'lightseagreen': (32, 178, 170, 1.0),
    'lightskyblue': (135, 206, 250, 1.0),
    'lightslategray': (119, 136, 153, 1.0),
    'lightslategrey': (119, 136, 153, 1.0),
    'lightsteelblue': (176, 196, 222, 1.0),
    'lightyellow': (255, 255, 224, 1.0),
    'lime': (0, 255, 0, 1.0),
    'limegreen': (50, 205, 50, 1.0),
    'linen': (250, 240, 230, 1.0),
    'magenta': (255, 0, 255, 1.0),
    'maroon': (128, 0, 0, 1.0),
    'mediumaquamarine': (102, 205, 170, 1.0),
    'mediumblue': (0, 0, 205, 1.0),
    'mediumorchid': (186, 85, 211, 1.0),
    'mediumpurple': (147, 112, 219, 1.0),
    'mediumseagreen': (60, 179, 113, 1.0),
    'mediumslateblue': (123, 104, 238, 1.0),
    'mediumspringgreen': (0, 250, 154, 1.0),
    'mediumturquoise': (72, 209, 204, 1.0),
    'mediumvioletred': (199, 21, 133, 1.0),
    'midnightblue': (25, 25, 112, 1.0),
    'mintcream': (245, 255, 250, 1.0),
    'mistyrose': (255, 228, 225, 1.0),
    'moccasin': (255, 228, 181, 1.0),
    'navajowhite': (255, 222, 173, 1.0),
    'navy': (0, 0, 128, 1.0),
    'oldlace': (253, 245, 230, 1.0),
    'olive': (128, 128, 0, 1.0),
    'olivedrab': (107, 142, 35, 1.0),
    'orange': (255, 165, 0, 1.0),
    'orangered': (255, 69, 0, 1.0),
    'orchid': (218, 112, 214, 1.0),
    'palegoldenrod': (238, 232, 170, 1.0),
    'palegreen': (152, 251, 152, 1.0),
    'paleturquoise': (175, 238, 238, 1.0),
    'palevioletred': (219, 112, 147, 1.0),
    'papayawhip': (255, 239, 213, 1.0),
    'peachpuff': (255, 218, 185, 1.0),
    'peru': (205, 133, 63, 1.0),
    'pink': (255, 192, 203, 1.0),
    'plum': (221, 160, 221, 1.0),
    'powderblue': (176, 224, 230, 1.0),
    'purple': (128, 0, 128, 1.0),
    'red': (255, 0, 0, 1.0),
    'rosybrown': (188, 143, 143, 1.0),
    'royalblue': (65, 105, 225, 1.0),
    'saddlebrown': (139, 69, 19, 1.0),
    'salmon': (250, 128, 114, 1.0),
    'sandybrown': (244, 164, 96, 1.0),
    'seagreen': (46, 139, 87, 1.0),
    'seashell': (255, 245, 238, 1.0),
    'sienna': (160, 82, 45, 1.0),
    'silver': (192, 192, 192, 1.0),
    'skyblue': (135, 206, 235, 1.0),
    'slateblue': (106, 90, 205, 1.0),
    'slategray': (112, 128, 144, 1.0),
    'slategrey': (112, 128, 144, 1.0),
    'snow': (255, 250, 250, 1.0),
    'springgreen': (0, 255, 127, 1.0),
    'steelblue': (70, 130, 180, 1.0),
    'tan': (210, 180, 140, 1.0),
    'teal': (0, 128, 128, 1.0),
    'thistle': (216, 191, 216, 1.0),
    'tomato': (255, 99, 71, 1.0),
    'turquoise': (64, 224, 208, 1.0),
    'violet': (238, 130, 238, 1.0),
    'wheat': (245, 222, 179, 1.0),
    'white': (255, 255, 255, 1.0),
    'whitesmoke': (245, 245, 245, 1.0),
    'yellow': (255, 255, 0, 1.0),
    'yellowgreen': (154, 205, 50, 1.0), 
}


def _parse_hex_color(color):
    """ Parse a CSS color string which starts with the '#' character.

    """
    int_ = int
    match = _HEX_RE.match(color)
    if match is not None:
        hex_str = match.group(1)
        if len(hex_str) == 3:
            r = int_(hex_str[0], 16)
            r |= (r << 4)
            g = int_(hex_str[1], 16)
            g |= (g << 4)
            b = int_(hex_str[2], 16)
            b |= (b << 4)
        else:
            r = int_(hex_str[:2], 16)
            g = int_(hex_str[2:4], 16)
            b = int_(hex_str[4:6], 16)
        return(r, g, b, 1.0)


def _parse_rgb_color(color):
    """ Parse a CSS color string which starts with the 'r' character.

    """
    int_ = int
    min_ = min
    max_ = max
    match = _RGB_NUM_RE.match(color)
    if match is not None:
        rs, gs, bs = match.groups()
        r = max_(0, min_(255, int_(rs)))
        g = max_(0, min_(255, int_(gs)))
        b = max_(0, min_(255, int_(bs)))
        return (r, g, b, 1.0)

    match = _RGB_PER_RE.match(color)
    if match is not None:
        rs, gs, bs = match.groups()
        r = max_(0, min_(100, int_(rs))) * 255 / 100 
        g = max_(0, min_(100, int_(gs))) * 255 / 100
        b = max_(0, min_(100, int_(bs))) * 255 / 100
        return (r, g, b, 1.0)

    float_ = float
    match = _RGBA_NUM_RE.match(color)
    if match is not None:
        rs, gs, bs, as_ = match.groups()
        r = max_(0, min_(255, int_(rs)))
        g = max_(0, min_(255, int_(gs)))
        b = max_(0, min_(255, int_(bs)))
        a = max_(0.0, min_(1.0, float_(as_)))
        return (r, g, b, a)

    match = _RGBA_PER_RE.match(color)
    if match is not None:
        rs, gs, bs, as_ = match.groups()
        r = max_(0, min_(100, int_(rs))) * 255 / 100 
        g = max_(0, min_(100, int_(gs))) * 255 / 100
        b = max_(0, min_(100, int_(bs))) * 255 / 100
        a = max_(0.0, min_(1.0, float_(as_)))
        return (r, g, b, a)


def _parse_hsl_color(color):
    """ Parse a CSS color string that starts with the 'h' character.

    """
    int_ = int
    min_ = min
    max_ = max
    match = _HSL_RE.match(color)
    if match is not None:
        hs, ss, ls = match.groups()
        h = (int_(hs) % 360 + 360) % 360
        s = max_(0, min_(100, int_(ss)))
        l = max_(0, min_(100, int_(ls)))
        a = 1.0
        r, g, b = hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
        return (int_(255 * r), int_(255 * g), int_(255 * b), a)

    match = _HSLA_RE.match(color)
    if match is not None:
        hs, ss, ls, as_ = match.groups()
        h = (int_(hs) % 360 + 360) % 360
        s = max_(0, min_(100, int_(ss)))
        l = max_(0, min_(100, int_(ls)))
        a = max_(0.0, min_(1.0, float(as_)))
        r, g, b = hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
        return (int_(255 * r), int_(255 * g), int_(255 * b), a)


#: A dispatch table of color parser functions.
_COLOR_PARSERS = {
    '#': _parse_hex_color,
    'r': _parse_rgb_color,
    'h': _parse_hsl_color,
}


def parse_color(color):
    """ Parse a color string into a tuple of RGBA values.

    Parameters
    ----------
    color : string
        A CSS3 string representation of the color.

    Returns
    -------
    result : tuple or None
        A tuple of RGBA values. The RGB values are integers in the
        range 0-255, and the alpha value is a float in the range
        0.0-1.0. If the string is invalid, None will be returned.

    """
    if color in _COLOR_TABLE:
        return _COLOR_TABLE[color]
    color = color.strip()
    if color:
        key = color[0]
        if key in _COLOR_PARSERS:
            return _COLOR_PARSERS[key](color)


def composite_colors(first, second):
    """ Composite two colors together using their given alpha.

    The first color will be composited on top of the second color.

    Parameters
    ----------
    first : tuple
        The rgba tuple of the first color. The rgb values should be
        ints in the range 0-255. The alpha value should be a float
        in the range 0.0-1.0.

    second : tuple
        The rgba tuple of the second color. The format of this tuple
        is the same as the first color.

    Returns
    -------
    result : tuple
        The composited rgba color tuple.

    """
    r1, g1, b1, a1 = first
    r2, g2, b2, a2 = second
    y = a2 * (1.0 - a1)
    ro = r1 * a1 + r2 * y
    go = g1 * a1 + g2 * y
    bo = b1 * a1 + b2 * y
    ao = a1 + y
    int_ = int
    return (int_(ro), int_(go), int_(bo), ao)

