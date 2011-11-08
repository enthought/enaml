#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime
import math

from abc import ABCMeta, abstractmethod


class Converter(object):
    """ Map values from an Enaml component to userspace models, and vice versa.

    Converters can be used to translate a values between the userspace models
    and the Enaml components or toolkit widgets. For example, a Converter can
    can be used to synchronize a Field's value with an integer attribute.

    Enaml provides several base Converters to be used with components like the
    Slider and Field. Custom converters can be created by subclassing and
    implementing the :meth:`to_component` and `from_component` methods.

    .. note:: To avoid race conditions and had to find bugs please ensure that
        'to_component' and 'from_component' are inverse functions. Thus the
        following expression is always valid::

            value == Converter.from_component(Converter.to_component(value))

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def to_component(self, value):
        """ Convert a value to be used by the Enaml component.

        """
        return NotImplemented

    @abstractmethod
    def from_component(self, value):
        """ Convert from the Enaml component to userspace models.

        """
        return NotImplemented

class PassThroughConverter(Converter):
    """ A simple pass throught converter.

    The converter just passes the values throught without acting uppon them.

    """
    def to_component(self, value):
        return value

    def from_component(self,value):
        return value

class BaseStringConverter(Converter):
    """ A simple abstract Converter that converts a userspace value to a string.

    The converter is an abstract class that defines only the to_component
    method. Subclasses need to implement the from_component method in order
    to have a fully functional Converter. Converters subclassing the
    :class:`BaseStringConverter` are suitable for use in Enaml Field
    components.

    """
    def to_component(self, value):
        return str(value)


class StringConverter(BaseStringConverter):
    """ A simple Converter that converts a userspace value to a string and back.

    .. note:: The class methods are only symmetric when the userspace value
        is a string. For other types a custom `from_component` method is needed.

    """
    def from_component(self, value):
        return str(value)


class IntConverter(BaseStringConverter):
    """ Convert an integer value to a string and back.

    """
    def from_component(self, value):
        return int(value)

class FloatConverter(BaseStringConverter):
    """ Convert a float value to a string and back.

    """
    def from_component(self, value):
        return float(value)


class HexConverter(BaseStringConverter):
    """ Convert between a string and a base-16 integer.

    """
    def to_component(self, value):
        return hex(value)

    def from_component(self, value):
        return int(value, 16)


class OctalConverter(BaseStringConverter):
    """ Convert from a widget to a base-8 integer, and back to an octal string.

    """
    def to_component(self, value):
        return oct(value)

    def from_component(self, value):
        return int(value, 8)


class SliderRangeConverter(Converter):
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
    """ Map the slider's range to a log scale.

    """
    def to_component(self, value):
        return math.log10(value)

    def from_component(self, value):
        return 10 ** value


class DateConverter(Converter):
    """ Convert between dates and strings.

    """
    def __init__(self, format_string='%Y-%m-%d'):
        """ Default the date format YYYY-MM-DD.

        """
        self.format_string = format_string

    def to_component(self, value):
        """ Convert from a date to a string.

        """
        return value.strftime(self.format_string)

    def from_component(self, value):
        """ Convert from a string to a date.

        """
        return datetime.datetime.strptime(value, self.format_string).date()


class DateTimeConverter(Converter):
    """ Convert between datetime objects and strings.

    """
    def __init__(self, format_string='%Y-%m-%dT%H:%M:%S'):
        """ Default to the ISO 8601 date and time format.

        Example
        -------
        >>> format_string = '%Y-%m-%dT%H:%M:%S'
        >>> datetime.datetime(2000, 02, 20, 14, 41).strftime(format_string)
        '2000-02-20T14:41:00'

        """
        self.format_string = format_string

    def to_component(self, value):
        """ Convert from a datetime to a string.

        """
        return value.strftime(self.format_string)

    def from_component(self, value):
        """ Convert from a string to a datetime.

        """
        return datetime.datetime.strptime(value, self.format_string)
