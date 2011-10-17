#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (Bool, Enum, Event, Instance, Property, Int,
                        cached_property, TraitError, Range)

from .control import IControlImpl, Control
from ..enums import Orientation, TickPosition

class ISliderImpl(IControlImpl):

    def parent_value_changed(self, value):
        raise NotImplementedError

    def parent__minimum_changed(self, minimum):
        raise NotImplementedError

    def parent__maximum_changed(self, maximum):
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

#: The maximum slider length
MAX_SLIDER_LENGHT = 1<<16

class Slider(Control):
    """ A simple slider widget.

    A slider can be used to select from a range of values.

    Attributes
    ----------
    value : Range(low='minimum', high='maximum')
        The position value of the Slider. The bounds are defined by
        :attr:minimum: and :attr:maximum:.

    minimum : Property(Int, 0)
        The minimum value for the index. To avoid issues where
        :attr:`minimum` is higher than :attr:`maximum`. The value is a 
        positive integer capped by the :attr:`maximum`. If the new value of
        :attr:`minimum` make the current position invalid then the current 
        position is set to :attr:minimum. Default value is 0.

    maximum : Property(Int, 100)
        The maximum value for the index. As before the value of
        :attr:`maximum` cannot be lower than :attr:`minimum`. If the new 
        value of :attr:`maximum` make the current position invalid then 
        the current position is set to :attr:maximum. The top value is 
        restricted to 65536, while the default is 100.

    length : Property(Int, depends_on=('minimum', 'maximum'))
        The length of the slider, a read only property that depends on
        :attr:`minimum` and :attr:`maximum`. The lenght value is used
        by a number of properties to adapt the slider appearence

    down : Property(Bool)
        A read only property which indicates whether or not the slider
        is pressed down.

    tracking : Bool
        If True, the value is updated while sliding. Otherwise, it is
        only updated when the slider is released. Defaults to True.

    single_step : Range(low=1, high='length')
        Defines the number of steps that the slider will move when the
        user presses the arrow keys. Default is 1.

    page_step : Range(low=1, high='length')
        Defines the number of steps that the slider will move when the
        user presses the page_up/page_down keys. Default is 10.

    tick_interval: Range(low=1, high='length', value=10, exclude_high=True)
        The interval to put between tick marks in slider range units.
        Default value is `10`.

    tick_position : TickPosition Enum value
        A TickPosition enum value indicating how to display the tick
        marks. Please note that the orientation takes precedence over
        the tick mark position and an incompatible tick position will
        be addapted according to the current orientation.

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

    _minimum : Int
        A protected attribute used by the implementation object to
        hold the validated slider minimum.

    _maximum : Int
        A protected attribute used by the implementation object to
        hold the validated slider maximum.

    """
    
    minimum = Property(Int)

    maximum = Property(Int)

    length = Property(Int, depends_on=('minimum', 'maximum'))

    value = Range(low='minimum', high='maximum')

    tracking = Bool(True)

    tick_interval = Range(low=1, high='length', value=10, exclude_high=True)

    single_step = Range(low=1, high='length')

    page_step = Range(low=1, high='length', value=10)

    tick_position = Enum(TickPosition.NO_TICKS, *TickPosition.values())

    orientation = Enum(Orientation.HORIZONTAL, *Orientation.values())

    pressed = Event

    released = Event

    moved = Event

    down = Property(Bool, depends_on='_down')

    _down = Bool

    _minimum = Int(0)

    _maximum = Int(100)

    #---------------------------------------------------------------------------
    # Overridden parent class taits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ISliderImpl)

    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down

    @cached_property
    def _get_length(self):
        """ The property getter for the 'length' attribute.

        """
        return self._maximum - self._minimum + 1

    def _set_minimum(self, value):
        """ Validate the assigment of the slider minimum.

        The minimum property should be positive and always smaller
        than :attr:`maximum`.

        """
        if  (0 <= value < self._maximum):
            # FIXME:
            # Because the Range Trait will not fire the change notifier when
            # when the dynamic bounds cause a change we will perform the check
            # our self and make sure the value_changed function is called.
            position = self.value                    
            if position < value:
                self.value = value
            self._minimum = value
        else:
            msg = ("The maximum value of the slider should be positive integer"
                   " and smaller than the current maximum ({0}), but a value of"
                   " {1} was given ".format(self._minimum, value))
            raise TraitError(msg)

    def _set_maximum(self, value):
        """ Validate the assigment of the slider maximum.

        The maximum property should be positive and always larger
        than :attr:`minimum`.

        """
        if  (self._minimum < value <= MAX_SLIDER_LENGHT):
            # FIXME:
            # Because the Range Trait will not fire the change notifier when
            # when the dynamic bounds cause a change we will perform the check
            # our self and make sure the value_changed function is called.
            position = self.value                    
            if position > value:
                self.value = value
            self._maximum = value
        else:
            msg = ("The minimum value of the slider should be positive integer"
                   " and larger than the current minimum ({0}), but a value of"
                   " {1} was given ".format(self._maximum, value))
            raise TraitError(msg)

    def _get_maximum(self):
        """ The property getter for the slider maximum.

        """
        return self._maximum

    def _get_minimum(self):
        """ The property getter for the slider minimum.

        """
        return self._minimum


Slider.protect('down', 'pressed', 'released', 'moved', '_down', 'length',
        'minimum', 'maximum', '_minimum', '_maximum')

