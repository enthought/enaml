from traits.api import Int, Event

from .i_element import IElement


class ISpinBox(IElement):
    """An interface for spin box widgets.

    Need a good way of differentiating between Float and Int spin boxes.    

    Different methods/Events for increase and decrease?

    """

    # The minimum value for this spin box.
    min_val = Int

    # The maximum value for this spin box.
    max_val = Int

    # The current value.
    value = Int

    # The amount by which `value` can change in a single step.
    step = Int

    # The event fired when this box's `value` is updated.
    changed = Event
