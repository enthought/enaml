#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Interface, Int, Tuple


class IGeometry(Interface):
    """ The position and size of an element.

    Attributes
    ----------
    x : Int
        The absolute x-coordinate of an element (in pixels).

    y : Int
        The absolute y-coordinate of an element (in pixels).

    position : Tuple
        An (x, y) tuple of an element's absolute position (in pixels).

    width : Int
        An Int representing the width of an element, in pixels.

    height : Int
        An Int representing the height of an element, in pixels.

    size : Tuple
        A Tuple of (width, height), with signs relative to position.

    """
    x = Int
    
    y = Int
    
    position = Tuple(Int, Int)
    
    width = Int
    
    height = Int
    
    size = Tuple(Int, Int)
    
    # The ability to transpose axes might be added later.
    #transform = XXX
