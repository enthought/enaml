from traits.api import Any, Bool, Callable, Enum, Float, Range

from ..constants import Ticks
from .i_element import IElement


class ISlider(IElement):
    """ A slider widget.

    Attributes
    ----------
    down : Bool
        Whether or not the slider is pressed down.

    from_slider : Callable
        A conversion function to convert from the slider postion
        to the appropriate Python value.
    
    to_slider : Callable
        A conversion function to convert from the slider position
        to the appropriate Python value.

    slider_pos : Float
        The floating point percentage (0.0 - 1.0) which is the 
        position of the slider. This is always updated while
        sliding.

    value : Any
        The value of the slider. This is set to the value of
        from_slider(slider_pos).

    tracking : Bool
        If True, the value is updated while sliding. Otherwise,
        it is only updated when the slider is released.

    tick_interval : Float
        The slider_pos interval to put between tick marks.

    ticks : Enum
        A Ticks enum value indicating how to display the 
        tick marks.

    sliding : Bool
        Will be True when the slider is sliding, False otherwise.

    Notes
    -----
    A slider's range is fixed at 0.0 to 1.0. Therefore, the 
    position of the slider can be viewed as a percentage. 
    To facilitate various ranges, you can specify from_pos
    and to_pos callables to convert to and from the position
    the value.

    """
    down = Bool
    
    from_slider = Callable(lambda pos: pos)
    
    to_slider = Callable(lambda val: val)
    
    slider_pos = Range(0.0, 1.0)
    
    value = Any
    
    tracking = Bool(True)
        
    tick_interval = Float

    ticks = Enum(Ticks.DEFAULT, Ticks.values())
    
    sliding = Bool

    # XXX - orientation should be contained on a compound object.
    
    #--------------------------------------------------------------------------
    # Features of QSlider which I'm not sure we should include.
    #--------------------------------------------------------------------------

    # The multi tick step for paging
    #multi_step = Float
    # The single tick step for the slider for arrow presses
    #single_step = Float


