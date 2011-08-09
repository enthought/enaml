from traits.api import List, Any, Event

from .i_element import IElement


class IStackedWidget(IElement):
    """A stack of widgets, with only one visible element at a time."""

    # A List of widgets that can be displayed.
    items = List
    
    # The visible widget in this stack.
    current_item = Any

    # The event fired when a different element is moved to the top.
    reordered = Event
