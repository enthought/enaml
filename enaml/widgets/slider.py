#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Enum, Property, Int, Either, Range

from .constraints_widget import PolicyEnum
from .control import Control


class Slider(Control):
    """ A simple slider widget that can be used to select from a range
    of integral values.

    A `SliderTransform` can be used to transform the integer range
    of the slider into another data space. For more details, see
    `enaml.stdlib.slider_transform`.

    """
    #: The minimum slider value. If the minimum value is changed such
    #: that it becomes greater than the current value or the maximum
    #: value, then those values will be adjusted. The default is 0.
    minimum = Property(Int)

    #: The internal minimum value storage.
    _minimum = Int(0)

    #: The maximum slider value. If the maximum value is changed such
    #: that it becomes smaller than the current value or the minimum
    #: value, then those values will be adjusted. The default is 100.
    maximum = Property(Int)

    #: The internal maximum storage.
    _maximum = Int(100)

    #: The position value of the Slider. The value will be clipped to
    #: always fall between the minimum and maximum.
    value = Property(Int)

    #: The internal value storage.
    _value = Int(0)

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
    orientation = Enum('horizontal', 'vertical')

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
    def snapshot(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        snap = super(Slider, self).snapshot()
        snap['minimum'] = self.minimum
        snap['maximum'] = self.maximum
        snap['value'] = self.value
        snap['single_step'] = self.single_step
        snap['page_step'] = self.page_step
        snap['tick_position'] = self.tick_position
        snap['tick_interval'] = self.tick_interval
        snap['orientation'] = self.orientation
        snap['tracking'] = self.tracking
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Slider, self).bind()
        attrs = (
            'minimum', 'maximum', 'value', 'single_step', 'page_step',
            'tick_position', 'tick_interval', 'orientation', 'tracking',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_value_changed(self, content):
        """ Handle the 'value_changed' action from the client widget.

        The content will contain the 'value' of the slider.

        """
        self.set_guarded(value=content['value'])

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

    def _set_minimum(self, minimum):
        """ The property setter for the 'minimum' attribute.

        """
        # Manually fire the trait change notifications to avoid the
        # need for property depends_on; this saves memory overhead.
        # All data is accessed using the private attributes to avoid
        # inadvertantly triggering the evaluation of a bound Enaml
        # attribute, which could fool with the state by setting the
        # value too soon.
        old_max = self._maximum
        if minimum > old_max:
            self._maximum = minimum
            self.trait_property_changed('maximum', old_max, minimum)
        old_val = self._value
        if minimum > old_val:
            self._value = minimum
            self.trait_property_changed('value', old_val, minimum)
        old_min = self._minimum
        if minimum != old_min:
            self._minimum = minimum
            self.trait_property_changed('minimum', old_min, minimum)

    def _get_maximum(self):
        """ The property getter for the slider 'maximum'.

        """
        return self._maximum

    def _set_maximum(self, maximum):
        """ The property setter for the 'maximum' attribute.

        """
        # Manually fire the trait change notifications to avoid the
        # need for property depends_on; this saves memory overhead.
        # All data is accessed using the private attributes to avoid
        # inadvertantly triggering the evaluation of a bound Enaml
        # attribute, which could fool with the state by setting the
        # value too soon.
        old_min = self._minimum
        if maximum < old_min:
            self._minimum = maximum
            self.trait_property_changed('minimum', old_min, maximum)
        old_val = self._value
        if maximum < old_val:
            self._value = maximum
            self.trait_property_changed('value', old_val, maximum)
        old_max = self._maximum
        if maximum != old_max:
            self._maximum = maximum
            self.trait_property_changed('maximum', old_max, maximum)

    def _get_value(self):
        """ The property getter for the slider 'value'.

        """
        return self._value

    def _set_value(self, value):
        """ The property setter for the 'value' attribute.

        """
        # Manually fire the trait change notifications to avoid the
        # need for property depends_on; this saves memory overhead.
        # The minimum and maximum values are explicity accessed through
        # their property so that any bound Enaml attributes can provide
        # the proper default value. This ensures that the min and max
        # are alway up-to-date before potentially clipping the value.
        old_val = self._value
        new_val = max(self.minimum, min(self.maximum, value))
        if old_val != new_val:
            self._value = new_val
            self.trait_property_changed('value', old_val, new_val)

