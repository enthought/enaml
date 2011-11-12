#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .color import Color

# XXX this class is stubbed out to handle brush style, but the style
# part is not yet implemented
class Brush(tuple):
    """ A tuple subclass which represents a toolkit independent painter
    brush.

    """
    __slots__ = ()

    def __new__(cls, color=Color.from_string('none'), style=None):
        if not isinstance(color, Color):
            raise TypeError('Expected Color instance, got %s' % color)
        return tuple.__new__(cls, (color, style))
    
    @property
    def color(self):
        return self[0]
    
    @property
    def style(self):
        return self[1]

