#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import TraitType, Interface, TraitError

from ..converters import Converter

class SubClass(TraitType):

    def __init__(self, cls):
        super(SubClass, self).__init__()
        if issubclass(cls, Interface):
            self.info = (cls, True)
        else:
            self.info = (cls, False)

    def validate(self, obj, name, value):
        cls, interface = self.info
        if interface:
            if issubclass(value.__implements__, cls):
                return value
        else:
            if issubclass(value, cls):
                return value
        if interface:
            msg = 'Class must be and implementor of %s.' % cls
            raise TypeError(msg)
        else:
            msg = 'Class must be a subclass of %s.' % cls
            raise TypeError(msg)


class ReadOnlyConstruct(TraitType):

    def __init__(self, factory):
        super(ReadOnlyConstruct, self).__init__()
        self._factory = factory

    def get(self, obj, name):
        dct = obj.__dict__
        if name in dct:
            res = dct[name]
        else:
            res = dct[name] = self._factory(obj, name)
        return res


class NamedLookup(TraitType):

    def __init__(self, lookup_func_name):
        super(NamedLookup, self).__init__()
        self._lookup_func_name = lookup_func_name

    def get(self, obj, name):
        return getattr(obj, self._lookup_func_name)(name)


class ORStr(TraitType):
    """ Allows a space-separated string of any combination of the
    constituents of the string passed to the constructor.

    i.e. StrFlags("foo bar") will validate only the following strings:

        "", "foo", "foo bar", "bar", "bar foo"

    """
    default_value = ""

    def __init__(self, allowed):
        self.allowed = set(allowed.strip().split())

    def is_valid(self, val):
        if not isinstance(val, basestring):
            return False
        components = val.strip.split()
        allowed = self.allowed
        return all(component in allowed for component in components)


class Bounded(TraitType):
    """ Generic Bounded Trait class.

    The class defines a generic Trait where the value is validated
    to be between low and high (static or dynamic) bounds. Where the
    limits can be any python object that supports comparison. Optionally
    the validation takes place after the input value has been converted
    with the converter function. In that case the low and high bounds are
    relative to the converter(value) result.

    """

    info_text = "Bounded value"

    def __init__(self, value, low=None, high=None, converter=None, **metadata):
        """
        Arguments
        ---------
        value :
            The default value.

        low :
            The lower bound of the Trait

        high :
            The upper bound of the Trait

        converter : (optional)
            Function to apply to convert assigned value before validation


        .. todo:: Force type on the value attribute


        """
        if value is None:
            if low is not None:
                value = low
            else:
                value = high

        super(Bounded, self).__init__(value, **metadata)

        if converter is None:
            converter = lambda val: val

        self._high = high
        self._low = low
        self._converter = converter


    def validate(self, obj, name, value):
        """ Validate the trait value.

        """
        converted_value = self.convert(obj, value)
        low, high = self.get_bounds(obj)

        if low is None:
            low = converted_value

        if high is None:
            high = converted_value

        if (low <= converted_value <= high):
            return value
        else:
            msg = ('The value (after convertion) must be a bounded value'
                   ' between {0} and {1}, but instead the converted'
                   ' result (of the input value {2}) was {3}'.\
                   format(low, high, value, converted_value))
            raise TraitError(msg)

    def convert(self, obj, value):
        """ Convert the input value for validation.

        .. note:: The method supports dynamic values (class traits).

        """
        converter = self._converter
        if isinstance(converter, basestring):
            converter = eval('obj.' + converter)

        if isinstance(converter, Converter):
            converter = converter.to_component

        try:
            converted_value = converter(value)
        except Exception as raised_exception:
            msg = ("The convertion failed with the following error: {0}".\
                   format(raised_exception))
            raise TraitError(msg)
        else:
            return converted_value

    def get_bounds(self, obj):
        """ Get the lower and upper bounds of the Trait

        .. note:: The method supports dynamic values (class traits).

        """
        low, high = self._low, self._high
        if isinstance(low, basestring):
            low = eval('obj.' + low)

        if isinstance(high, basestring):
            high = eval('obj.' + high)

        return low, high
