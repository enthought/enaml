#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import math
from abc import ABCMeta, abstractmethod

class Converter(object):
    """ Map values from an Enaml component to a model, and vice versa.

    Some Enaml components store a Converter as a public attribute.
    Converters can be used to translate a value between a toolkit widget
    and some other form.

    For example, use a Converter to synchronize a Field's value with an
    integer attribute, or to scale a slider's value beyond the interval
    (0.0, 1.0).

    Enaml provides several Converters. Subclass a Converter for custom
    behavior. Subclasses must implement both the 'to_component' and
    'from_component' functions.

    .. note:: Please ensure that 'to_component' and 'from_component' are inverse
       functions. Thus the following experssion should be always valid::

            value == Converter.from_component(Converter.to_component(value))

       Failure to follow this advice can result in infinite recursion.

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def to_component(self, value):
        """ Convert to a value that a toolkit widget can understand.

        Parameters
        ----------
        value
            A value for use by a toolkit widget.

        """
        return NotImplemented

    @abstractmethod
    def from_component(self, value):
        """ Convert a widget's value for display or some other use.

        Parameters
        ----------
        value
            A value from a toolkit widget.

        """
        return NotImplemented


class PassThroughConverter(Converter):
    """ A simple pass throught converter.

    The converter just passes the values throught without acting uppon them

    """
    def to_component(self, value):
        return value

    def from_component(self,value):
        return value


class StringConverter(Converter):
    """ A simple Converter that converts any value to a string.

    """
    def to_component(self, value):
        return str(value)

    def from_component(self, value):
        return str(value)


class IntConverter(Converter):
    """ Convert from a widget to a base-10 integer, and back to a string.

    This can be used for integer Fields.

    """
    def to_component(self, value):
        return str(value)

    def from_component(self, value):
        return int(value)


class HexConverter(IntConverter):
    """ Convert from a widget to a base-16 integer, and back to a hex string.

    """
    def to_component(self, value):
        return hex(value)

    def from_component(self, value):
        return int(value, 16)


class OctalConverter(IntConverter):
    """ Convert from a widget to a base-8 integer, and back to an octal string.

    """
    def to_component(self, value):
        return oct(value)

    def from_component(self, value):
        return int(value, 8)


class FloatConverter(Converter):
    """ Convert from a widget to a float, and back to a string.

    This can be used for float Fields.

    """
    def to_component(self, value):
        return str(value)

    def from_component(self, value):
        return float(value)

class SliderRangeConverter(FloatConverter):
    """ Map a slider's value onto an interval other than (0.0, 1.0).

    """
    def __init__(self, low, high):
        self.low = low
        self.high = high

    def to_component(self, value):
        low = self.low
        return (value - low) / float(self.high - low)

    def from_component(self, value):
        low = self.low
        return float(value * (self.high - low) + low)

class SliderLogConverter(Converter):
    """ Map the slider's range to a log scale

    """
    def to_component(self, value):
        return math.log10(value)

    def from_component(self, value):
        return 10 ** value
