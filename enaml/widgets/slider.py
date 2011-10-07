#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (Any, Bool, Callable, Enum, Float, Range, Event,
                        Instance, Property, Int, Either)

from .control import IControlImpl, Control
from ..converters import Converter, PassThroughConverter
from ..enums import Orientation, TickPosition


class ISliderImpl(IControlImpl):

    def parent_convert_changed(self, converter):
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
    ranges, you can specify a Converter class to convert to and from the
    position the value.

    Attributes
    ----------
    value : Any
        The value of the slider.  When the slider is moved, the value is set
        to the result of from_slider.  If the value is changed, then the
        result of to_slider is used to position the slider

    convert : Instance(Converter)
        A converter that will convewrt between the value attribute and a
        floating point number in the interval (0.0, 1.0) that is used
        internaly by the slider component.

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

    """
    down = Property(Bool, depends_on='_down')

    value = Any

    convert = Instance(Converter, factory=PassThroughConverter)

    tracking = Bool(True)

    tick_interval = Float(0.1)

    single_step = Int(1)

    page_step = Int(5)

    tick_position = Enum(TickPosition.NO_TICKS, *TickPosition.values())

    orientation = Enum(Orientation.HORIZONTAL, *Orientation.values())

    pressed = Event

    released = Event

    moved = Event

    _down = Bool

    #---------------------------------------------------------------------------
    # Overridden parent class taits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ISliderImpl)

    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down


Slider.protect('down', 'pressed', 'released', 'moved', '_down')

