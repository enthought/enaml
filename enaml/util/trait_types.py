#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import TraitType, Interface, TraitError, Any
from traits.traits import CTrait


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
    on assigment to fall between low and high (static or dynamic) bounds.

    """
    info_text = "Bounded value"

    def __init__(self, value=None, low=None, high=None, **metadata):
        """
        Arguments
        ---------
        value :
            The default value. It can be a python object or a Trait.

        low :
            The lower bound of the Trait.

        high :
            The upper bound of the Trait.

        """
        if isinstance(value, CTrait):
            default_value = value.default
        else:
            default_value = value

        super(Bounded, self).__init__(default_value, **metadata)

        self._high = high
        self._low = low

        if (isinstance(value, CTrait)) and (value is not Any):
            self._value_type = value
            self.validate = self.validate_with_trait
        else:
            self.validate = self.validate_bounds

    def validate_with_trait(self, obj, name, value):
        """ Validate the trait value.

        Validation takes place in two steps:
        #. The input value is validated based on the expected Trait type.
        #. The value it is between the static (or dynamic) bounds.

        """
        value_type = self._value_type
        value = value_type.validate(obj, name, value)
        return self.validate_bounds(obj, name, value)

    def validate_bounds(self, obj, name, value):
        """ Validate that the value is in range.

        .. note:: Any exceptions that may take place are converted to
            TraitErrors.

        """
        low, high = self.get_bounds(obj)
        if low is None:
            low = value
        if high is None:
            high = value
        is_inside_bounds = False
        try:
            is_inside_bounds = (low <= value <= high)
        except Exception as raised_exception:
            if isinstance(raised_exception, TraitError):
                raise raised_exception
            else:
                msg = ("Bound checking of {0} caused a the following Python "
                       "Exception: {1}").format(value, raised_exception)
                raise TraitError(msg)
        if not is_inside_bounds:
            msg = ('The assigned date value of must be bounded between {0} '
                   ' and {1}, the input value was {2}'.\
                   format(low, high, value))
            raise TraitError(msg)

        return value

    def get_bounds(self, obj):
        """ Get the lower and upper bounds of the Trait.

        .. note:: The method supports dynamic values (class traits).

        """
        low, high = self._low, self._high
        if isinstance(low, basestring):
            low = reduce(getattr, low.split('.'), obj)

        if isinstance(high, basestring):
            high = reduce(getattr, high.split('.'), obj)

        return low, high
