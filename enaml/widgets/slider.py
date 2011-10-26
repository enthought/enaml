#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (Bool, Enum, Event, Instance, Property, Int, 
                        TraitError, Range)

from .control import Control, AbstractTkControl

from ..enums import Orientation, TickPosition


class AbstractTkSlider(AbstractTkControl):

    @abstractmethod
    def shell_value_changed(self, value):
        raise NotImplementedError
    
    @abstractmethod
    def shell_minimum_changed(self, minimum):
        raise NotImplementedError
    
    @abstractmethod
    def shell_maximum_changed(self, maximum):
        raise NotImplementedError
    
    @abstractmethod
    def shell_tracking_changed(self, tracking):
        raise NotImplementedError
    
    @abstractmethod
    def shell_single_step_changed(self, single_step):
        raise NotImplementedError
    
    @abstractmethod
    def shell_page_step_changed(self, page_step):
        raise NotImplementedError

    @abstractmethod
    def shell_tick_interval_changed(self, tick_interval):
        raise NotImplementedError

    @abstractmethod
    def shell_tick_position_changed(self, tick_position):
        raise NotImplementedError

    @abstractmethod
    def shell_orientation_changed(self, orientation):
        raise NotImplementedError


#: The maximum slider value
MAX_SLIDER_VALUE = (1 << 16) - 1


class Slider(Control):
    """ A simple slider widget.

    A slider can be used to select from a range of values.

    """
    #: The minimum value for the index. To avoid issues where
    #: :attr:`minimum` is higher than :attr:`maximum`. The value is 
    #: a positive integer capped by the :attr:`maximum`. If the new 
    #: value of :attr:`minimum` make the current position invalid then 
    #: the current position is set to :attr:minimum. Default value is 0.
    minimum = Property(Int, depends_on ='_minimum')

    #: The internal minimum storage
    _minimum = Int(0)

    #: The maximum value for the index. Checks make sure that
    #: :attr:`maximum` cannot be lower than :attr:`minimum`. If the 
    #: new value of :attr:`maximum` make the current position invalid 
    #: then the current position is set to :attr:maximum. The max value 
    #: is restricted to 65535, while the default is 100.
    maximum = Property(Int, depends_on ='_maximum')

    #: The internal maximum storage
    _maximum = Int(100)

    #: The span of the slider, a read only property that depends on
    #: :attr:`minimum` and :attr:`maximum`. The span value is used
    #: by a number of properties that adapt the slider's appearence.
    span = Property(Int, depends_on=('minimum', 'maximum'))

    #: The position value of the Slider. The bounds are defined by
    #: :attr:minimum: and :attr:maximum:.
    value = Range(low='minimum', high='maximum')

    #: The interval to put between tick marks in slider range units.
    #: Default value is `10`.
    tick_interval = Range(low=1, high='span', value=10, exclude_high=True)

    #: Defines the number of steps that the slider will move when the
    #: user presses the arrow keys. Default is 1.
    single_step = Range(low=1, high='span', value=1)

    #: Defines the number of steps that the slider will move when the
    #: user presses the page_up/page_down keys. Default is 10.
    page_step = Range(low=1, high='span', value=10)

    #: A TickPosition enum value indicating how to display the tick
    #: marks. Please note that the orientation takes precedence over
    #: the tick mark position and an incompatible tick position will
    #: be addapted according to the current orientation.
    tick_position = Enum(TickPosition.NO_TICKS, *TickPosition.values())

    #: The orientation of the slider. The default orientation is
    #: horizontal. When the orientation is flipped the tick positions
    #: (if set) also adapt to reflect the changes  (e.g. the LEFT
    #: becomes TOP when the orientation becomes horizontal).
    orientation = Enum(Orientation.HORIZONTAL, *Orientation.values())

    #: If True, the value is updated while sliding. Otherwise, it is
    #: only updated when the slider is released. Defaults to True.
    tracking = Bool(True)

    #: Fired when the slider is pressed.
    pressed = Event

    #: Fired when the slider is released.
    released = Event

    #: Fired when the slider is moved.
    moved = Event

    #: A read only property which indicates whether or not the slider
    #: is pressed down.
    down = Property(Bool, depends_on='_down')

    #: The internal down storage
    _down = Bool

    #: Overridden parent class tait
    abstract_obj = Instance(AbstractTkSlider)

    #--------------------------------------------------------------------------
    # Property methods
    #--------------------------------------------------------------------------
    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down

    def _get_span(self):
        """ The property getter for the 'length' attribute.

        """
        return (self.maximum - self.minimum) + 1

    def _set_minimum(self, value):
        """ Validate the assigment of the slider minimum.

        The minimum property should be positive and always smaller
        than :attr:`maximum`.

        """
        if  (value < 0) or (value > self.maximum):
            msg = ("The minimum value of the slider should be a positive "
                   "integer and smaller than the current maximum ({0}), "
                   "but a value of {1} was given")
            msg = msg.format(self.maximum, value)
            raise TraitError(msg)

        # FIXME:
        # Because the Range Trait will not fire the change notifier when
        # the dynamic bounds cause a change we will perform the check
        # and make sure the value_changed function is called.
        position = self.value
        if position < value:
            self.value = value
        self._minimum = value

    def _set_maximum(self, value):
        """ Validate the assigment of the slider maximum.

        The maximum property should be positive and always larger
        than :attr:`minimum`.

        """
        if  (value < self.minimum) or (value > MAX_SLIDER_VALUE):
            msg = ("The maximum value of the slider should be a positive "
                   "integer and larger than the current minimum ({0}), "
                   "but a value of {1} was given")
            msg = msg.format(self.minimum, value)
            raise TraitError(msg)

        # FIXME:
        # Because the Range Trait will not fire the change notifier when
        # the dynamic bounds cause a change we will perform the check
        # and make sure the value_changed function is called.
        position = self.value
        if position > value:
            self.value = value
        self._maximum = value

    def _get_maximum(self):
        """ The property getter for the slider maximum.

        """
        return self._maximum

    def _get_minimum(self):
        """ The property getter for the slider minimum.

        """
        return self._minimum

