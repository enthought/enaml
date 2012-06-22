#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    Bool, Property, Int, TraitError, Either, Range, on_trait_change,
)

from enaml.core.trait_types import Bounded, EnamlEvent
from enaml.enums import Orientation, TickPosition, PolicyEnum

from .control import Control


#: The maximum slider value
MAX_SLIDER_VALUE = (1 << 16) - 1


class Slider(Control):
    """ A simple slider widget that can be used to select from a 
    range of values.

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
    value = Bounded(low='minimum', high='maximum')

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
    #: marks. Note that the orientation takes precedence over the tick 
    #: mark position and an incompatible tick position will be adapted 
    #: according to the current orientation. The default tick position
    #: is 'bottom'.
    tick_position = TickPosition('bottom')

    #: The orientation of the slider. The default orientation is
    #: horizontal. When the orientation is flipped the tick positions
    #: (if set) also adapt to reflect the changes  (e.g. the LEFT
    #: becomes TOP when the orientation becomes horizontal).
    orientation = Orientation

    #: If True, the value is updated while sliding. Otherwise, it is
    #: only updated when the slider is released. Defaults to True.
    tracking = Bool(True)

    #: Fired when the slider is pressed.
    pressed = EnamlEvent

    #: Fired when the slider is released.
    released = EnamlEvent

    #: Fired when the user drags the slider handle via the mouse.
    #: The event payload will be the position of the slider. This is
    #: always fired regardless of the value of :attr:`tracking`
    moved = EnamlEvent

    #: A read only property which indicates whether or not the slider
    #: is pressed down.
    down = Property(Bool, depends_on='_down')

    #: The internal down storage
    _down = Bool

    #: Hug width is redefined as a property to be computed based on the 
    #: orientation of the slider unless overridden by the user.
    hug_width = Property(PolicyEnum, depends_on=['_hug_width', 'orientation'])

    #: Hug height is redefined as a property to be computed based on the 
    #: orientation of the slider unless overridden by the user.
    hug_height = Property(PolicyEnum, depends_on=['_hug_height', 'orientation'])

    #: An internal override trait for hug_width
    _hug_width = Either(None, PolicyEnum, default=None)

    #: An internal override trait for hug_height
    _hug_height = Either(None, PolicyEnum, default=None)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Slider, self).bind()
        self.default_send(
            'maximum', 'minimum', 'orientation', 'page_step', 'single_step',
            'tick_interval', 'tick_position', 'tracking', 'value'
        )

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(Slider, self).initial_attrs()
        attrs = {
            'maximum' : self.maximum,
            'minimum' : self.minimum,
            'orientation' : self.orientation,
            'page_step' : self.page_step,
            'single_step' : self.single_step,
            'tick_interval' : self.tick_interval,
            'tick_position' : self.tick_position,
            'tracking' : self.tracking,
            'value' : self.value,
        }
        super_attrs.update(attrs)
        return super_attrs

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def receive_moved(self, context):
        """ Callback from the UI when the control is moved.

        """
        self.moved()

    def receive_pressed(self, context):
        """ Callback from the UI when the control is pressed.

        """
        self._down = True
        self.pressed()

    def receive_released(self, context):
        """ Callback from the UI when the control is released.

        """
        self._down = False
        self.released()

    def receive_set_value(self, context):
        """ Callback from the UI when the slider's value changes

        """
        self.set_guarded(value=context['value'])
    
    #--------------------------------------------------------------------------
    # Trait defaults
    #--------------------------------------------------------------------------
    def _get_hug_width(self):
        """ The proper getter for 'hug_width'. Returns a computed hug 
        value unless overridden by the user.

        """
        res = self._hug_width
        if res is None:
            if self.orientation == 'horizontal':
                res = 'ignore'
            else:
                res = 'strong'
        return res

    def _get_hug_height(self):
        """ The proper getter for 'hug_width'. Returns a computed hug 
        value unless overridden by the user.

        """
        res = self._hug_height
        if res is None:
            if self.orientation == 'vertical':
                res = 'ignore'
            else:
                res = 'strong'
        return res

    def _set_hug_width(self, value):
        """ The property setter for 'hug_width'. Overrides the computed
        value.

        """
        self._hug_width = value

    def _set_hug_height(self, value):
        """ The property setter for 'hug_height'. Overrides the computed
        value.

        """
        self._hug_height = value

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
        """ The property setter for the 'minimum' attribute. This
        validates that the value is always smaller than :attr:`maximum`.

        """
        if  (value < 0) or (value > self.maximum):
            msg = ('The minimum value of the slider should be a positive '
                   'integer and smaller than the current maximum ({0}), '
                   'but a value of {1} was given')
            msg = msg.format(self.maximum, value)
            raise TraitError(msg)
        else:
            self._minimum = value

    def _set_maximum(self, value):
        """ The property setter for the 'maximum' attribute. This
        validates that the value is always larger than :attr:`minimum`.

        """
        if  (value < self.minimum) or (value > MAX_SLIDER_VALUE):
            msg = ("The maximum value of the slider should be a positive "
                   "integer and larger than the current minimum ({0}), "
                   "but a value of {1} was given")
            msg = msg.format(self.minimum, value)
            raise TraitError(msg)
        else:
            self._maximum = value

    def _get_maximum(self):
        """ The property getter for the slider maximum.

        """
        return self._maximum

    def _get_minimum(self):
        """ The property getter for the slider minimum.

        """
        return self._minimum

    @on_trait_change('minimum, maximum')
    def _adapt_value(self):
        """ Adapt the value to the boundaries

        """
        if self.initialized:
            self.value = min(max(self.value, self.minimum), self.maximum)

