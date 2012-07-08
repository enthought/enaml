#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    Bool, Property, Int, Float, TraitError, Either, Range, on_trait_change,
    Enum,
)

from enaml.core.trait_types import Bounded

from .constraints_widget import ConstraintsWidget, PolicyEnum


#: The slider attributes to proxy to clients
_SLIDER_ATTRS = [
    'maximum', 'minimum', 'orientation', 'page_step', 'single_step',
    'tick_interval', 'tick_position', 'tracking', 'value'
]


#: The maximum slider value. Somewhat arbitrary, but the limit in Qt.
MAX_SLIDER_VALUE = (1 << 16) - 1


class Slider(ConstraintsWidget):
    """ A simple slider widget that can be used to select from a range 
    of integral values.

    """
    #: The minimum value for the slider. To avoid issues where
    #: :attr:`minimum` is higher than :attr:`maximum`. The value is
    #: a positive integer capped by the :attr:`maximum`. If the new
    #: value of :attr:`minimum` make the current position invalid then
    #: the current position is set to :attr:minimum. Default value is 0.
    minimum = Property(Int, depends_on ='_minimum')

    #: The internal minimum storage.
    _minimum = Int(0)

    #: The maximum value for the slider. Checks make sure that
    #: :attr:`maximum` cannot be lower than :attr:`minimum`. If the
    #: new value of :attr:`maximum` make the current position invalid
    #: then the current position is set to :attr:maximum. The max value
    #: is restricted to 65535, while the default is 100.
    maximum = Property(Int, depends_on ='_maximum')

    #: The internal maximum storage.
    _maximum = Int(100)

    #: The position value of the Slider. The bounds are defined by
    #: :attr:minimum: and :attr:maximum:.
    value = Bounded(low='minimum', high='maximum')

    #: Defines the number of steps that the slider will move when the
    #: user presses the arrow keys. The default is 1. An upper limit 
    #: may be imposed according the limits of the client widget.
    single_step = Range(low=1)

    #: Defines the number of steps that the slider will move when the
    #: user presses the page_up/page_down keys. The Default is 10. An
    #: upper limit may be imposed on this value according to the limits
    #: of the client widget.
    page_step = Range(low=1, value=10)

    #: A TickPosition enum value indicating how to display the tick
    #: marks. Note that the orientation takes precedence over the tick 
    #: mark position and an incompatible tick position will be adapted 
    #: according to the current orientation. The default tick position
    #: is 'bottom'.
    tick_position = Enum( 
        'bottom', ('no_ticks', 'left', 'right', 'top', 'bottom', 'both'),
    )

    #: The interval to place between slider tick marks in units of
    #: value (as opposed to pixels). The minimum value is 0, which
    #: indicates that the choice is left up to the client.
    tick_interval = Range(low=0)

    #: The orientation of the slider. The default orientation is
    #: horizontal. When the orientation is flipped the tick positions
    #: (if set) also adapt to reflect the changes  (e.g. the LEFT
    #: becomes TOP when the orientation becomes horizontal).
    orientation = Enum(('horizontal', 'vertical'))

    #: If True, the value is updated while sliding. Otherwise, it is
    #: only updated when the slider is released. Defaults to True.
    tracking = Bool(True)
    
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
    def creation_attributes(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(Slider, self).creation_attributes()
        for attr in _SLIDER_ATTRS:
            super_attrs[attr] = getattr(self, attr)
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Slider, self).bind()
        self.publish_attributes(*_SLIDER_ATTRS)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_event_changed(self, payload):
        """ Handle the 'event-changed' action from the client widget.
        The payload will contain the 'value' of the slider.

        """
        self.set_guarded(value=payload['value'])

    #--------------------------------------------------------------------------
    # Property Methods
    #--------------------------------------------------------------------------
    def _get_hug_width(self):
        """ The property getter for 'hug_width'. 

        Returns a computed hug value unless overridden by the user.

        """
        res = self._hug_width
        if res is None:
            if self.orientation == 'horizontal':
                res = 'ignore'
            else:
                res = 'strong'
        return res

    def _get_hug_height(self):
        """ The proper getter for 'hug_height'. 

        Returns a computed hug value unless overridden by the user.

        """
        res = self._hug_height
        if res is None:
            if self.orientation == 'vertical':
                res = 'ignore'
            else:
                res = 'strong'
        return res

    def _set_hug_width(self, value):
        """ The property setter for 'hug_width'. 

        Overrides the computed value.

        """
        self._hug_width = value

    def _set_hug_height(self, value):
        """ The property setter for 'hug_height'. 

        Overrides the computed value.

        """
        self._hug_height = value

    def _get_minimum(self):
        """ The property getter for the slider 'minimum'.

        """
        return self._minimum

    def _set_minimum(self, value):
        """ The property setter for the 'minimum' attribute. 

        This validates that the value is always smaller than 
        :attr:`maximum`.

        """
        if value > self.maximum:
            msg = ('The minimum value of the slider should be smaller '
                   'than the current maximum ({0}), but a value of {1} '
                   'was given')
            msg = msg.format(self.maximum, value)
            raise TraitError(msg)
        else:
            self._minimum = value

    def _get_maximum(self):
        """ The property getter for the slider 'maximum'.

        """
        return self._maximum

    def _set_maximum(self, value):
        """ The property setter for the 'maximum' attribute. 

        This validates that the value is always larger than
        :attr:`minimum`.

        """
        if  (value < self.minimum) or (value > MAX_SLIDER_VALUE):
            msg = ('The maximum value of the slider should be larger '
                   'than the current minimum ({0}) and less than the '
                   'maximum slider value ({1}), but a value of {2} '
                   'was given')
            msg = msg.format(self.minimum, MAX_SLIDER_VALUE, value)
            raise TraitError(msg)
        else:
            self._maximum = value

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @on_trait_change('minimum, maximum')
    def _adapt_value(self):
        """ Adapt the value to the min/max boundaries.

        """
        if self.initialized:
            self.value = min(max(self.value, self.minimum), self.maximum)

