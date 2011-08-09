from traits.api import List, Int

from .i_element import IElement


class IStackedWidget(IElement):
    """A stack of widgets, with only one visible element at a time."""

    # A List of widgets that can be displayed.
    elements = List
    
    # Index in the `elements` list of the visible widget in this stack.
    current_index = Int
