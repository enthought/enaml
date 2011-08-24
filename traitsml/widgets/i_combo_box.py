from traits.api import Dict, Any, Event, Bool, Str, Callable

from .i_element import IElement


class IComboBox(IElement):
    """ A drop-down list from which one item can be selected at a time.

    Use a combo box to select a single item from a collection of
    items. To select multiple items from a collection of items
    use a List widget.
    
    Attributes
    ----------
    items : Dict(Str, Any)
        Maps the string representations of the items in the collection
        to the items themselves.

    value : Any
        The currently selected item from the collection.

    sort : Bool
        Whether or not to sort the choices for display.

    sort_key : Callable
        If sort is True, this sort key will be used. The keys in
        the items dict will be passed as arguments to the key. 
        The default key sorts by ascii order.
    
    opened : Bool
        Set to True when the combo box is opened, False otherwise.

    selected : Event
        Fired when a new selection is made. The args object will
        contain the selection.

    clicked : Event
        Fired when the combo box is clicked.

    """
    items = Dict(Str, Any)

    value = Any

    sort = Bool

    sort_key = Callable(lambda val: val)

    opened = Bool

    selected = Event

    clicked = Event

