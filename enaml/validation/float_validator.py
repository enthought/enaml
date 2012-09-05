#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Either, Float, Bool

from .validator import Validator


class FloatValidator(Validator):
    """ A concrete Validator which handles floating point input.

    This validator ensures that the text represents a floating point
    number within a specified range.

    """
    #: The minimum value allowed for the float, inclusive, or None if 
    #: there is no lower bound.
    minimum = Either(None, Float)

    #: The maximum value allowed for the float, inclusive, or None if 
    #: there is no upper bound.
    maximum = Either(None, Float)

    #: Whether or not to allow exponents like '1e6' in the input.
    allow_exponent = Bool(True)
    
    def convert(self, text):
        """ Converts the text to a floating point value.

        Parameters
        ----------
        text : unicode
            The unicode text to convert to an integer.

        Returns
        -------
        result : float
            The floating point value for the converted text. 

        Raises
        ------
        ValueError
            A ValueError will be raised if the conversion fails.

        """
        return float(text)

    def validate(self, text, component):
        """ Validates the given text matches the float range.

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
        try:
            value = self.convert(text)
        except ValueError:
            return (text, False)
        minimum = self.minimum
        if minimum is not None and value < minimum:
            return (text, False)
        maximum = self.maximum
        if maximum is not None and value > maximum:
            return (text, False)
        if not self.allow_exponent and 'e' in text.lower():
            return (text, False)
        return (text, True)

    def client_validator(self):
        """ The client side float validator.

        Returns
        -------
        result : dict
            The dict representation of the client side float validator.
            
        """
        res = {}
        res['type'] = 'float'
        res['message'] = self.message
        res['arguments'] = {
            'minimum': self.minimum,
            'maximum': self.maximum,
            'allow_exponent': self.allow_exponent
        }
        return res

