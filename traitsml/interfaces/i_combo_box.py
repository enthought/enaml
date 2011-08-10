from traits.api import List, Any, Event, Bool

from .i_element import IElement


class IComboBox(IElement):
    """A dropdown list, from which one item can be selected at a time."""

    # The available choices for this combo box.
    items = List

    # The current selection.
    value = Any

    # Visible items: just the current selection (False), or a choice (True).
    open = Bool
    
    # The event fired when a new value is selected.
    selected = Event

    # The event fired when a combo box is clicked.
    clicked = Event

