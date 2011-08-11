from traits.api import Interface, Int, Tuple, Enum

from ..constants import Layout


class ILayout(Interface):
    """A configurable representation of an element's layout."""
    
    # The current type of layout, e.g., VERTICAL.
    mode = Enum(Layout.DEFAULT, *Layout.values())

    # The space between an element's border and other elements' margins.
    margin = Int
    
    # The space between an element's border and its inner content.
    padding = Int

    # The (x, y) coordinate location of an element in a grid.
    grid_coords = Tuple(Int, Int)
    
    # The number of rows and columns that an element spans in a grid.
    grid_span = Tuple(Int, Int)
    
    # The ordinal position of an element in a one-dimensional layout.
    index = Int
    
    # The priority of an element in stacking along the z-axis.
    # If (A.z_axis > B.z_axis), then element A will appear above B.
    z_index = Int
