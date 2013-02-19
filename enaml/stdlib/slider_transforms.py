#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Enaml Standard Library - Slider Transforms

This module contains declarative classes which can be used as children
of a `Slider` to transform the integer range of the slider into an
alternative data space.

"""
from atom.api import Value, Bool, Float, Range

from enaml.core.declarative import Declarative, d_properties


class SliderTransform(Declarative):
    """ A base class for creating declarative slider transforms.

    A SliderTransform must be subclassed to be useful. The abstract api
    defined below must be implemented by the subclass.

    When using a transform with a slider, the transform takes complete
    ownership of the slider range. That is, no effort is made to listen
    for outside changes to the slider range, so all changes should be
    made on the transform.

    """
    __slots__ = '__weakref__'

    #: The data-space minimum for the transform. This may be redefined
    #: by a subclass to enforce stronger typing.
    minimum = Value()

    #: The data-space maximum for the transform. This may be redefined
    #: by a subclass to enforce stronger typing.
    maximum = Value()

    #: The data-space value for the transform. This may be redefined
    #: by a subclass to enforce stronger typing.
    value = Value()

    #: A boolean flag used to prevent loopback cycles.
    _guard = Bool(False)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def initialize(self):
        """ An initialization handler.

        The parent slider values are initialized during the transform
        initialization pass.

        """
        self._apply_transform()
        super(SliderTransform, self).initialize()
        parent = self.parent
        if parent is not None:
            parent.observe('value', self._update_value)

    def _apply_transform(self, minimum=True, maximum=True, value=True):
        """ Apply the current transform to the parent slider.

        Parameters
        ----------
        minimum : bool, optional
            Whether or not to update the slider minimum. The default
            is False.

        maximum : bool, optional
            Whether or not to update the slider maximum. The default
            is False.

        value : bool, optional
            Whether or not to update the slider value. The default
            is False.

        """
        parent = self.parent
        if parent is not None:
            if minimum:
                parent.minimum = self.get_minimum()
            if maximum:
                parent.maximum = self.get_maximum()
            if value:
                parent.value = self.get_value()

    def _update_value(self, change):
        """ Update the transformed value when slider changes.

        """
        if self.is_initialized:
            self._guard = True
            try:
                self.set_value(change.new)
            finally:
                self._guard = False

    def _observe_minimum(self, change):
        """ Update the slider minimum on transform minimum change.

        """
        if self.is_initialized:
            self._apply_transform(maximum=False, value=False)

    def _observe_maximum(self, change):
        """ Update the slider maximum on transform maximum change.

        """
        if self.is_initialized:
            self._apply_transform(minimum=False, value=False)

    def _observe_value(self, change):
        """ Update the slider value on transform value change.

        """
        if self.is_initialized and not self._guard:
            self._apply_transform(minimum=False, maximum=False)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def get_minimum(self):
        """ Get the minimum value of the transform as an int.

        Returns
        -------
        result : int
            The minimum value of the transform converted to an int.

        """
        raise NotImplementedError

    def get_maximum(self):
        """ Get the maximum value of the transform as an int.

        Returns
        -------
        result : int
            The maximum value of the transform converted to an int.

        """
        raise NotImplementedError

    def get_value(self):
        """ Get the value of the transform as an int.

        Returns
        -------
        result : int
            The value of the transform converted to an int.

        """
        raise NotImplementedError

    def set_value(self, value):
        """ Set the value of the transform from an int.

        Parameters
        ----------
        value : int
            The integer value of the slider.

        """
        raise NotImplementedError


@d_properties('minimum', 'maximum', 'value', 'precision')
class FloatTransform(SliderTransform):
    """ A concreted SliderTransform for floating point values.

    """
    #: A redeclared parent class member which enforces float values.
    minimum = Float(0.0)

    #: A redeclared parent class member which enforces float values.
    maximum = Float(1.0)

    #: A redeclared parent class member which enforces float values.
    value = Float(0.0)

    #: The number of stops to use between the minimum and maximum.
    precision = Range(low=1, value=100)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def get_minimum(self):
        """ Get the minimum value of the transform as an int.

        Returns
        -------
        result : int
            The minimum value of the transform converted to an int.

        """
        return 0

    def get_maximum(self):
        """ Get the maximum value of the transform as an int.

        Returns
        -------
        result : int
            The maximum value of the transform converted to an int.

        """
        return self.precision

    def get_value(self):
        """ Get the value of the transform as an int.

        Returns
        -------
        result : int
            The value of the transform converted to an int.

        """
        offset = self.value - self.minimum
        delta = self.maximum - self.minimum
        return int(offset * self.precision / delta)

    def set_value(self, val):
        """ Set the value of the transform from an int.

        Parameters
        ----------
        value : int
            The integer value of the slider.

        """
        delta = self.maximum - self.minimum
        self.value = (val * delta / self.precision) + self.minimum

