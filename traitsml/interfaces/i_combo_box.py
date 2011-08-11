from traits.api import Dict, Any, Event, Bool, Str, Callable

from .i_element import IElement


class IComboBox(IElement):
    """ A drop-down list from which one item can be selected at a time.
    
    Attributes
    ----------
    items : Dict
        Maps the string representations of the choices to the
        the choices themselves.

    value : Any
        The current selection.

    sort : Bool
        Whether or not to sort the choices for display.

    sort_key : Callable
        If sort is True, this sort key will be used.

    active : Bool
        Whether or not the combo box is currently dropped down.

    selected : Event
        Fired when a new selection is made.

    clicked : Event
        Fired when the combo box is clicked.

    """
    items = Dict(Str, Any)

    value = Any

    sort = Bool

    sort_key = Callable

    active = Bool

    selected = Event

    clicked = Event


