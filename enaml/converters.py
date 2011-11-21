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


class IntConverter(BaseStringConverter):
    """ Convert an integer value to a string and back.

    """
    def from_component(self, value):
        return int(value)


class LongConverter(BaseStringConverter):
    """ Convert an long integer value to a string and back.

    """
    def from_component(self, value):
        return long(value)


class FloatConverter(BaseStringConverter):
    """ Convert a float value to a string and back.

    """
    def from_component(self, value):
        return float(value)


class ComplexConverter(BaseStringConverter):
    """ Convert a complex value to a string and back.

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
    """ Convert from a widget to a base-8 integer.

    """
    def to_component(self, value):
        return oct(value)

    def from_component(self, value):
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

