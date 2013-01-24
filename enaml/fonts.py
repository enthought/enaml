#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A utility module for dealing with fonts.

"""
from collections import namedtuple


#: Keywords and regexes used for font parsing
_styles = set(['normal', 'italic', 'oblique'])
_variants = set(['normal', 'small-caps'])
_weights = set([
    'normal', 'bold', 'bolder', 'lighter', '100', '200', '300', '400',
    '500', '600', '700', '800', '900'
])
_sizes = set([
    'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large',
    'larger', 'smaller',
])
_units = set(['in', 'cm', 'mm', 'pt', 'pc', 'px'])


Font = namedtuple('Font', 'style variant weight size family')


def parse_font(font):
    """ Parse a CSS font string into a Font namedtuple.

    The parsing performed here is a bit more forgiving on bad values
    than the standard defined by CSS.

    Returns
    -------
    result : Font
        A namedtuple of font information for the given string.

    """
    style = 'normal'
    variant = 'normal'
    weight = 'normal'
    size = 'medium'
    family = ''
    for part in font.split():
        if part in _styles:
            style = part
        elif part in _variants:
            variant = part
        elif part in _weights:
            weight = part
        elif part in _sizes:
            size = part
        else:
            if part[-1] == '%':
                try:
                    float(part[:-1])
                except ValueError:
                    pass
                else:
                    size = part
            elif part[-2:] in _units:
                try:
                    float(part[:-2])
                except ValueError:
                    pass
                else:
                    size = part
            else:
                family = part
    return Font(style, variant, weight, size, family)

