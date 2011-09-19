#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (Any, Bool, Callable, Enum, Float, Range, Event,
                        Instance, Property, Int, Either)

from .control import IControlImpl, Control

from ..enums import Orientation, TickPosition


class ISliderImpl(IControlImpl):

    def parent_from_slider_changed(self, from_slider):
        raise NotImplementedError

    def parent_to_slider_changed(self, to_slider):
        raise NotImplementedError

    def parent_value_changed(self, value):
        raise NotImplementedError

    def parent_tracking_changed(self, tracking):
        raise NotImplementedError

    def parent_single_step_changed(self, single_step):
        raise NotImplementedError

    def parent_page_step_changed(self, page_step):
        raise NotImplementedError

    def parent_tick_interval_changed(self, tick_interval):
        raise NotImplementedError

    def parent_tick_position_changed(self, tick_position):
        raise NotImplementedError

    def parent_orientation_changed(self, orientation):
        raise NotImplementedError


class Slider(Control):
    """ A simple slider widget.

    A slider can be used to select from a continuous range of values.
    The slider's range is fixed at 0.0 to 1.0. Therefore, the position
    of the slider can be viewed as a percentage. To facilitate various
    ranges, you can specify from_pos and to_pos callables to convert to
    and from the position the value.

    Attributes
    ----------
    from_slider : Callable
        A function that takes one floating point argument in the range 0.0 - 1.0
        and converts from to the appropriate Python value.

    to_slider : Callable
        A function that takes one argument to convert from a Python
        value to the appropriate value in the range 0.0 - 1.0.

    value : Any
        The value of the slider.  When the slider is moved, the value is set
        to the result of from_slider.  If the value is changed, then the
        result of to_slider is used to position the slider

    down : Property(Bool)
        A read only property which indicates whether or not the slider
        is pressed down.

    tracking : Bool
        If True, the value is updated while sliding. Otherwise, it is
        only updated when the slider is released. Defaults to True.

    single_step : Int
        Defines the number of ticks that the slider will move when the
        user presses the arrow keys. Default is 1

    page_step : Int
        Defines the number of ticks that the slider will move when the
        user presses the page_up/page_down keys. Default is 5

    tick_interval : Range(0.0, 1.0, 0.1, exclude_low=True, exclude_high=True)
        The interval to put between tick marks in slider range units.
        Default value is `0.1` which is 10% of the full slider range.

    tick_position : TickPosition Enum value
        A TickPosition enum value indicating how to display the tick
        marks. Please note that the orientation takes precedence over
        the tick mark position and if for example the user sets the tick
        to an invalid value it is ignored. The ticks option BOTH is not
        supported yet in the wx backend, and will be also ignored.

    orientation : Orientation Enum value
        The orientation of the slider. The default orientation is
        horizontal. When the orientation is flipped the tick positions
        (if set) also adapt to reflect the changes  (e.g. the LEFT
        becomes TOP when the orientation becomes horizontal).

    pressed : Event
        Fired when the slider is pressed.

    released : Event
        Fired when the slider is released.

    moved : Event
        Fired when the slider is moved.

    _down : Bool
        A protected attribute used by the implementation object to
        update the value of down.

    .. note:: The slider enaml widget changes the attributes and fires
        the necessary events in sequence based on their priority as
        given below (from highest to lowest):

            # update `slider_pos` (when changed by the ui) or `value`
              (when changed programatically).
            # fire `invalid_value`.
            # fire `moved`.
            # update `down`.
            # fire pressed.
            # fire released.

    """
    down = Property(Bool, depends_on='_down')

    from_slider = Callable(lambda pos: pos)

    to_slider = Callable(lambda val: val)
    
    value = Any

    tracking = Bool(True)

    tick_interval = Float(0.1)

    single_step = Int(1)

    page_step = Int(5)

    tick_position = Enum(TickPosition.BOTTOM, *TickPosition.values())

    orientation = Enum(*Orientation.values())

    pressed = Event

    released = Event

    moved = Event

    invalid_value = Event

    _down = Bool

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ISliderImpl)

    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down

    def _validate(self, value):
        if self.validate_slider is not None:
            return self.validate_slider(value)
        
        try:
            slider = self.to_slider(value)
            return isinstance(slider, float) and 0.0 <= slider <= 1.0
        except Exception, e:
            logging.exception('Slider Validation: to_slider() raised exception:', e)
            return False
 
Slider.protect('down', 'pressed', 'released', 'moved', 'invalid_value', '_down')

