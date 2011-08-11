from traits.api import List, Any, Event

from .i_element import IElement


class IStackedWidget(IElement):
    """ A stack of widgets, with only one visible widget at a time. 

    Attributes
    ----------
    items : List
       A group of Widgets, with only one shown.

    current_item : Any
        The visible widget in this stack.

    reordered = Event
        Fired when a different element is moved to the top.

    """
    items = List
    
    current_item = Any

    reordered = Event

