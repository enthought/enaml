#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Str, Unicode, Int, Bool, Enum, Either, \
    Property, cached_property

from .client_validators import regex_validator, int_range_validator, \
    float_range_validator, regex_preprocessor

#------------------------------------------------------------------------------
#  Validator classes
#------------------------------------------------------------------------------

class Validator(HasTraits):
    """ The base class for creating widget text validators.

    This class is abstract. It's abstract api must be implemented by a
    subclass in order to be usable.

    """
    #: An optional message to associate with the validator. This message
    #: will be sent to the client widget if server side validation fails
    message = Unicode

    def validate(self, text, component):
        """ Validates the given text.

        This is an abstract method which must be implemented by 
        sublasses.

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        component : Declarative
            The declarative component currently making use of the
            validator.

        Returns
        -------
        result : (unicode, bool)
            A 2-tuple of (optionally modified) unicode text, and whether
            or not that text should be considered valid.

        """
        raise NotImplementedError

    def client_validator(self):
        """ A serializable representation of a client side validator.

        Returns
        -------
        result : dict or None
            A dict in the format specified by 'validator_format.js'
            or None if no client validator is specified. The default
            implementation of this method returns None.

        """
        return None


class RegexValidator(Validator):
    """ A concrete Validator implementation which validates using a
    regular expression.

    """
    #: The regular expression string to use for validation. The default
    #: regex matches everything.
    regex = Str(r'.*')

    #: A read only cached property which holds a preprocessed arguments.
    _cached_arguments = Property(depends_on='regex')

    @cached_property
    def _get__cached_arguments(self):
        """ The getter for the '_validator' property. 

        Returns
        -------
        result : function
            A function that takes text and returns True if the regex matches
            the text.

        """
        return regex_preprocessor(self.regex)

    def validate(self, text, component):
        """ Validates the given text matches the regular expression.

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        component : Declarative
            The declarative component currently making use of the
            validator.

        Returns
        -------
        result : (unicode, bool)
            A 2-tuple of (optionally modified) unicode text, and whether
            or not that text should be considered valid.

        """
        validity = regex_validator(text, **self._cached_arguments)
        return (text, validity)
 

    def client_validator(self):
        """ The client side regex validator.

        Returns
        -------
        result : dict
            The dictionary representation of a client side regex
            validator for the current regular expression.
            
        """
        res = {}
        res['type'] = 'regex'
        res['message'] = self.message
        res['arguments'] = {'regex': self.regex}
        return res


class IntRangeValidator(Validator):
    """ A concrete Validator implementation which ensures that the text
    converts to an integer in a certain range in a specified base.

    """

    #: The minimum value of the range, inclusive, or None if no lower bound.
    minimum = Either(None, Int)

    #: The maximum value of the range, inclusive, or None if no upper bound.
    maximum = Either(None, Int)

    #: The base that the integer is represented.
    base = Enum(10, 2, 8, 16)
    
    def validate(self, text, component):
        """ Validates the given text matches the integer range.

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        component : Declarative
            The declarative component currently making use of the
            validator.

        Returns
        -------
        result : (unicode, bool)
            A 2-tuple of (optionally modified) unicode text, and whether
            or not that text should be considered valid.

        """
        validity = int_range_validator(text, self.base, self.minimum,
            self.maximum)
        return (text, validity)

    def client_validator(self):
        """ The client side regex validator.

        Returns
        -------
        result : dict
            The dictionary representation of a client side int_range
            validator for the current arguments.
            
        """
        res = {}
        res['type'] = 'int_range'
        res['message'] = self.message
        res['arguments'] = {
            'minimum': self.minimum,
            'maximum': self.maximum,
            'base': self.base
        }
        return res


class FloatRangeValidator(Validator):
    """ A concrete Validator implementation which ensures that the text
    converts to a float in a certain range with a specified precision.

    """

    #: The minimum value of the range, inclusive, or None if no lower bound.
    minimum = Either(None, Int)

    #: The maximum value of the range, inclusive, or None if no upper bound.
    maximum = Either(None, Int)
    
    #: The number of places to allow after the decimal point.  None
    #: indicates arbitrary precision.
    precision = Either(None, Int)

    #: Whether or not to allow scientific notation in the input.
    allow_scientific_notation = Bool
    
    def validate(self, text, component):
        """ Validates the given text matches the integer range.

        Parameters
        ----------
        text : unicode
            The unicode text edited by the client widget.

        component : Declarative
            The declarative component currently making use of the
            validator.

        Returns
        -------
        result : (unicode, bool)
            A 2-tuple of (optionally modified) unicode text, and whether
            or not that text should be considered valid.

        """
        validity = float_range_validator(text, self.minimum, self.maximum,
            self.precision, self.allow_scientific_notation)
        return (text, validity)

    def client_validator(self):
        """ The client side regex validator.

        Returns
        -------
        result : dict
            The dictionary representation of a client side float_range
            validator for the current arguments.
            
        """
        res = {}
        res['type'] = 'float_range'
        res['message'] = self.message
        res['arguments'] = {
            'minimum': self.minimum,
            'maximum': self.maximum,
            'precision': self.precision,
            'allow_scientific_notation': self.allow_scientific_notation
        }
        return res

