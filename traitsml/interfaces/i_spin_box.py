from traits.api import Int, Float, Either, Event

from .i_element import IElement


class ISpinBox(IElement):
    """An interface for spin box widgets.

    Use `step` to differentiate between Float and Int spin boxes?

    Different methods/Events for increase and decrease?

    """

    # The minimum value for this spin box.
    min_val = Either(Int, Float)

    # The maximum value for this spin box.
    max_val = Either(Int, Float)

    # The current value.
    value = Either(Int, Float)

    # The amount by which `value` can change in a single step.
    step = Either(Int, Float)

    # The event fired when this box's `value` is updated.
    changed = Event
