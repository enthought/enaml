from traits.api import (Any, Bool, Callable, Enum, Float, Range, Event, 
                        Instance, Property)

from .control import IControlImpl, Control

from ..enums import Orientation, TickPosition
from ..util.decorators import protected


class ISliderImpl(IControlImpl):

    def parent_from_slider_changed(self, from_slider):
        raise NotImplementedError
    
    def parent_to_slider_changed(self, to_slider):
        raise NotImplementedError
    
    def parent_value_changed(self, value):
        raise NotImplementedError
    
    def parent_tracking_changed(self, tracking):
        raise NotImplementedError
    
    def parent_tick_interval_changed(self, tick_interval):
        raise NotImplementedError
    
    def parent_tick_position_changed(self, tick_position):
        raise NotImplementedError
    
    def parent_orientation_changed(self, orientation):
        raise NotImplementedError
    

@protected('_down', '_slider_pos', )
class Slider(Control):
    """ A simple slider widget.

    A slider can be used to select from a continuous range of values.
    The slider's range is fixed at 0.0 to 1.0. Therefore, the position 
    of the slider can be viewed as a percentage. To facilitate various 
    ranges, you can specify from_pos and to_pos callables to convert to 
    and from the position the value.

    Attributes
    ----------
    down : Property(Bool)
        A read only property which indicates whether or not the slider 
        is pressed down.

    from_slider : Callable
        A function that takes one argument to convert from the slider 
        postion to the appropriate Python value.
    
    to_slider : Callable
        A function that takes one argument to convert from a Python 
        value to the appropriate slider position.

    slider_pos : Property(Float)
        A read only property which is the floating point percentage 
        (0.0 - 1.0) which is the position of the slider. This value 
        is always updated while the slider is moving.

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

    _down : Bool
        A protected attribute used by the implementation object to 
        update the value of down.
    
    _slider_pos : Range(0.0, 1.0)
        A protected attribute used by the implementation object to
        update the value of slider_pos.

    """
    down = Property(Bool, depends_on='_down')
    
    from_slider = Callable(lambda pos: pos)
    
    to_slider = Callable(lambda val: val)
    
    slider_pos = Property(Float, depends_on='_slider_pos')
    
    value = Any
    
    tracking = Bool(True)
        
    tick_interval = Float

    ticks = Enum(*TickPosition.values())

    orientation = Enum(*Orientation.values())

    pressed = Event

    released = Event

    moved = Event

    _down = Bool

    _slider_pos = Range(0.0, 1.0)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ISliderImpl)

    def _get_down(self):
        return self._down
    
    def _get_slider_pos(self):
        return self._slider_pos

    
