from traits.api import Interface, Int, Tuple, Enum

from ..constants import Layout


class ILayout(Interface):
    """ A configurable representation of an element's layout.

    Attributes
    ----------
    mode : Enum
        The current type of layout, e.g., vertical.

    margin : Int
        The space between an element's border and other elements' margins.

    padding : Int
        The space between an element's border and its inner content.

    grid_coords : Tuple
        The (x, y) coordinate location of an element in a grid.

    grid_span : Tuple
        The number of rows and columns that an element spans in a grid.

    index : Int
        The ordinal position of an element in a one-dimensional layout.

    z_index : Int
        The priority of an element in stacking along the z-axis.
        If (A.z_axis > B.z_axis), then element A will appear above B.

    """    
    mode = Enum(Layout.DEFAULT, *Layout.values())

    margin = Int
   
    padding = Int

    grid_coords = Tuple(Int, Int)
    
    grid_span = Tuple(Int, Int)
    
    index = Int
    
    z_index = Int
