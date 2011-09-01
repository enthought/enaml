from traits.api import Any, Bool, Callable, Enum, Float, Range, Event

from .i_element import IElement

from ..enums import Orientation, TickPosition


class ISlider(IElement):
    """ A simple slider widget.

    A slider can be used to select from a continuous range of values.
    The slider's range is fixed at 0.0 to 1.0. Therefore, the position
    of the slider can be viewed as a percentage. To facilitate various
    ranges, you can specify from_pos and to_pos callables to convert to
    and from the position the value.

    Attributes
    ----------
    down : Bool
        Whether or not the slider is pressed down.

    from_slider : Callable
        A function that takes one argument to convert from the slider
        position to the appropriate Python value.

    to_slider : Callable
        A function that takes one argument to convert from a Python
        value to the appropriate slider position.

    slider_pos : Float
        The floating point percentage (0.0 - 1.0) which is the position
        of the slider. This value is always updated while the slider is
        moving.

    value : Any
        The value of the slider. This is set to the value of
        from_slider(slider_pos).

    tracking : Bool
        If True, the value is updated while sliding. Otherwise, it is
        only updated when the slider is released. Defaults to True.

    tick_interval : Float
        The slider_pos interval to put between tick marks.

    tick_position : TickPosition Enum value
        A TickPosition enum value indicating how to display the tick
        marks.

    orientation : Orientation Enum value
        The orientation of the slider. One of the Orientation enum
        values.

    pressed : Event
        Fired when the slider is pressed.

    released : Event
        Fired when the slider is released.

    moved : Event
        Fired when the slider is moved.

    invalid_value: Event
        Fired when there was an attempt to assign an invalid (out of range)
        value to the slider

    """
    down = Bool

    from_slider = Callable(lambda pos: pos)

    to_slider = Callable(lambda val: val)

    slider_pos = Range(0.0, 1.0)

    value = Any

    tracking = Bool(True)

    tick_interval = Float

    ticks = Enum(*TickPosition.values())

    orientation = Enum(*Orientation.values())

    pressed = Event

    released = Event

    moved = Event

    invalid_value = Event


