from traits.api import Any, Bool, Callable, Enum, Float, Range

from ..constants import Orientation, TickPosition
from .i_element import IElement


class ISlider(IElement):
    
    # A slider's range is fixed at 0.0 to 1.0. Therefore, the 
    # position of the slider can be viewed as a percentage. 
    # To facilitate various ranges, you can specify from_pos
    # and to_pos callables to convert to and from the position
    # the value. By default, these callables are just pass through.

    # Whether or not the slider is pressed down
    down = Bool
    
    # The conversion function to convert from slider to value.
    from_slider = Callable(lambda pos: pos)
    
    # The multi tick step for paging
    multi_step = Float
    
    # The orientation of the slider
    orientation = Enum(Orientation.DEFAULT, *Orientation.values())
    
    # The floating point percentage (0.0 - 1.0) which is 
    # the position of the slider. Always updated while sliding.
    slider_pos = Range(0.0, 1.0)
    
    # The single tick step for the slider for arrow presses
    single_step = Float

    # The interval (value interval, not pixel interval) to put
    # between tick marks. The default is zero and indicates that
    # the toolkit can choose between single_step and multi_step.
    tick_interval = Float

    # Where to draw the ticks marks for the slider
    tick_pos = Enum(TickPosition.DEFAULT, TickPosition.values())
    
    # The conversion function to convert from value to slider.
    to_slider = Callable(lambda val: val)

    # Whether or not the value should be updated when sliding,
    # or only when the slider is released
    tracking = Bool(True)

    # The value of the slider. Will be set to from_pos(pos).
    # Changes to this value will update the position and vice-versa.
    value = Any

    
