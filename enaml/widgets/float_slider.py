#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Constant, Float, Property, Range, TraitError

from .slider import Slider, MAX_SLIDER_VALUE

_FLOAT_SLIDER_ATTRS = [
    'maximum', 'minimum', 'orientation', 'page_step', 'precision',
    'single_step', 'tick_interval', 'tick_position', 'tracking', 'value'
]


class FloatSlider(Slider):
    """ A simple slider widget that can be used to select from a range
    of float values.

    """
    #: The minimum value for the slider. To avoid issues where
    #: :attr:`minimum` is higher than :attr:`maximum`. The value is
    #: a positive integer capped by the :attr:`maximum`. If the new
    #: value of :attr:`minimum` make the current position invalid then
    #: the current position is set to :attr:`minimum`. Default value
    #: is 0.0.
    minimum = Property(Float, depends_on='_minimum')

    #: The internal minimum storage.
    _minimum = Float(0.0)

    #: The maximum value for the slider. Checks make sure that
    #: :attr:`maximum` cannot be lower than :attr:`minimum`. If the
    #: new value of :attr:`maximum` make the current position invalid
    #: then the current position is set to :attr:maximum. The max value
    #: defaults to 1.0.
    maximum = Property(Float, depends_on='_maximum')

    #: The internal maximum storage.
    _maximum = Float(1.0)

    #: The number of integer steps allowed by the slider. The max value
    #: is restricted to 65535, while the default is 100.
    precision = Range(value=100, low=1, high=MAX_SLIDER_VALUE)

    #: Defines the number of steps that the slider will move when the
    #: user presses the arrow keys. The default is 10. An upper limit
    #: may be imposed according the limits of the client widget.
    single_step = Range(low='_one', high='precision', value=10,
                        exclude_high=True)
    _one = Constant(1)

    #: Defines the number of steps that the slider will move when the
    #: user presses the page_up/page_down keys. The Default is 10. An
    #: upper limit may be imposed on this value according to the limits
    #: of the client widget.
    page_step = Range(low='_one', high='precision', value=10)

    #: The interval to place between slider tick marks in units of
    #: value (as opposed to pixels). This will be rounded to the nearest
    #: number of integer steps (based on :attr:`precision`). If this
    #: rounded value is zero, the interval choice is left up to the
    #: client.
    tick_interval = Range(low=0.0)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(Slider, self).snapshot()
        for attr in _FLOAT_SLIDER_ATTRS:
            snap[attr] = getattr(self, attr)
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Slider, self).bind()
        self.publish_attributes(*_FLOAT_SLIDER_ATTRS)

    #--------------------------------------------------------------------------
    # Property Methods
    #--------------------------------------------------------------------------
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
