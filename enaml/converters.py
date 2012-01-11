#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import datetime


class Converter(object):
    """ Map values from an Enaml component to userspace models and 
    vice versa.

    Converters can be used to translate a values between the userspace 
    models and the Enaml components or toolkit widgets. For example, a 
    Converter can be used to synchronize a Field's string value with an 
    integer attribute.

    Enaml provides several base Converters to be used with components 
    like the Field. Custom converters can be created by subclassing and
    implementing the :meth:`to_component` and `from_component` methods.

    .. note:: To avoid race conditions and hard to track bugs 
        'to_component' and 'from_component' should be inverse 
        functions. Thus the following expression should hold::

            val == Converter.from_component(Converter.to_component(val))

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_component(self, value):
        """ Convert a value to be used by the Enaml component. If the
        value cannot be converted, the method should raise a ValueError.

        """
        return NotImplemented

    @abstractmethod
    def from_component(self, value):
        """ Convert from the Enaml component to userspace models. If the
        value cannot be converted, the method should raise a ValueError.

        """
        return NotImplemented


class NullConverter(Converter):
    """ A simple pass through converter which does not perform any
    value modification.

    """
    def to_component(self, value):
        return value

    def from_component(self,value):
        return value


class BaseStringConverter(Converter):
    """ A simple abstract Converter that converts a userspace value 
    to a string.

    This is an abstract class that defines only the to_component method. 
    Subclasses need to implement the from_component method in order to
    have a fully functional Converter. Subclasses derived from this class
    are suitable for use in Enaml Field components.

    """
    def to_component(self, value):
        return str(value)


class StringConverter(BaseStringConverter):
    """ A simple Converter that converts a userspace value to a string 
    and back.

    .. note:: The class methods are only symmetric when the userspace 
        value is a string. For other types a custom `from_component` 
        method is needed.

    """
    def from_component(self, value):
        return str(value)


class RangeConverter(BaseStringConverter):
    """Base class for numeric fields with a data type that has a natural ordering.
    
    This class can not be instantiated.  Subclasses must implmented the
    type_convert method.
    """

    def __init__(self, low=None, high=None, allow_low=True, allow_high=True, **kwargs):
        self.low = low
        self.high = high
        self.allow_low = allow_low
        self.allow_high = allow_high
        super(RangeConverter, self).__init__(**kwargs)

    @abstractmethod
    def type_convert(self, value):
        """Convert from the string `value` to the desired data type.
        
        This is the basic type conversion, without bounds checking.

        Subclasses must define this method.
        """
        pass

    def _range_str(self):
        """Create a string the gives the range of this converter.
        
        Only call this function when at least one of self.low or self.high
        is not None.
        """
        s = []
        if self.low is not None:
            s.append(str(self.low))
            low_ineq_str = '<=' if self.allow_low else '<'
            s.append(low_ineq_str)
        s.append('value')
        if self.high is not None:
            high_ineq_str = '<=' if self.allow_high else '<'
            s.append(high_ineq_str)
            s.append(str(self.high))
        return ' '.join(s)

    def _out_of_range(self, value):
        """Return True if `value` does not satisy the bounds."""
        if (self.low is not None and
            (value < self.low or (value == self.low and not self.allow_low))):
            return True
        if (self.high is not None and
            (value > self.high or (value == self.high and not self.allow_high))):
            return True
        return False

    def from_component(self, value):
        val = self.type_convert(value)

        if self._out_of_range(val):
            raise ValueError(("value {} is outside the valid range for this "
                              "field: {}").format(val, self._range_str()))

        return val


class IntConverter(RangeConverter):
    """ Convert an integer value to a string and back.

    """
    def type_convert(self, value):
        """Convert the string `value` to an int."""
        return int(value)


class LongConverter(RangeConverter):
    """ Convert a long integer value to a string and back.

    """
    def type_convert(self, value):
        """Convert the string `value` to a long integer."""
        return long(value)


class FloatConverter(RangeConverter):
    """ Convert a float value to a string and back.

    """
    def type_convert(self, value):
        """Convert the string `value` to a float."""
        return float(value)


class ComplexConverter(BaseStringConverter):
    """ Convert a complex value to a string and back.

    """
    def from_component(self, value):
        return float(value)


class HexConverter(RangeConverter):
    """ Convert between a string and a base-16 integer.

    """

    def to_component(self, value):
        return hex(value)

    def type_convert(self, value):
        return int(value, 16)


class OctalConverter(RangeConverter):
    """ Convert from a widget to a base-8 integer.

    """

    def to_component(self, value):
        return oct(value)

    def type_convert(self, value):
        return int(value, 8)


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
