from traits.api import Dict, Any, Event, Bool, Str, Callable

from .i_element import IElement


class IComboBox(IElement):
    """ A drop-down list from which one item can be selected at a time.
    
    Attributes
    ----------
    items : dict. Maps the string representation of the choices to the
            the choices themselves.

    value : object. The current selection.

    sort : boolean. Whether or not to sort the choices for display.

    sort_key : callable. If sort is True, this sort key will be used.

    active : Bool.
        Whether or not the combo box is currently dropped down.

    selected : event. Fired when a new selection is made.

    clicked : event. Fired when the combo box is clicked.

    """
    items = Dict(Str, Any)

    value = Any

    sort = Bool

    sort_key = Callable

    active = Bool

    selected = Event

    clicked = Event


