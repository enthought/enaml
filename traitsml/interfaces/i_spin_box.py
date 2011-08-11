from traits.api import Int, Float, Either, Event

from .i_element import IElement


class ISpinBox(IElement):
    """ A spin box widget.
   
    Attributes
    ----------
    low : Int or Float
        The minimum value for the spin box.

    high : Int or Float
        The maximum value for the spin box.
    
    value : Int or Float
        The current value for the spin box.

    step : Int or Float
        The amount by which `value` can change in a single step.

    changed : Event
        Fired when the spin box value is updated.

    """
    min_val = Either(Int, Float)

    max_val = Either(Int, Float)

    value = Either(Int, Float)

    step = Either(Int, Float)

    changed = Event


