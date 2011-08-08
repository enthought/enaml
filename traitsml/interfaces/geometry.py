from traits.api import HasTraits, Int, Tuple


class Geometry(HasTraits):
    
    # The absolute x-coordinate of an element (in pixels).
    x = Int
    
    # The absolute y-coordinate of an element (in pixels).
    y = Int
    
    # An (x, y) Tuple of an element's absolute position (in pixels).
    position = Tuple(Int, Int)
    
    # An Int representing the width of an element, in pixels.
    width = Int
    
    # An Int representing the height of an element, in pixels.
    height = Int
    
    # A Tuple of (width, height), with signs relative to position.
    size = Tuple(Int, Int)
    
    # The ability to transpose axes might be added later.
    #transform = XXX
