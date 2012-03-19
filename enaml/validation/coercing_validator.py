#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .abstract_validator import AbstractValidator


class CoercingValidator(AbstractValidator):
    """ A concrete implementation of AbstractValidator which uses various
    callables to convert, coerce, and format between values and text. 

    This class serves as a base class for several other validators, such
    as the number and date/time validators. It does not on its own use 
    the provided locale object for conversions.

    A CoercingValidator instance will, by default, consider all inputs
    as valid and format all values according to their default unicode
    representation.

    """
    def __init__(self, converter=None, coercer=None, formatter=None, **kwargs):
        """ Initialize a CoercingValidator.

        Parameters
        ----------
        converter : callable or None, optional
            If provided, a callable which accepts the string value
            and returns a value to pass the coercing function. If not
            provided, a suitable default is used. Defaults to None.
        
        coercer : callable or None, optional
            If provided, a callable which accepts the evaluated value
            and returns a new coerced value to use for verifying 
            validity. If not provided, a suitable default is used. 
            Defaults to None.
        
        formatter : callable or None, optional
            If provided, a callable which accepts the context-dependent
            model value and returns a unicode string for display. If 
            not provided, a suitable default is used. Defaults to None.
        
        **kwargs
            The keyword arguments necessary to initialize an instance
            of AbstractValidator.

        """
        super(CoercingValidator, self).__init__(**kwargs)
        if converter is not None:
            self._convert = converter
        if coercer is not None:
            self._coerce = coercer
        if formatter is not None:
            self._format = formatter
    
    def _convert(self, text):
        """ The default method to convert the string to a number. This
        may be overridden by subclasses or through instance-specific
        attributes.
        
        """
        return text
         
    def _coerce(self, value):
        """ The default method to coerce the given value into a value 
        to test for validity. This may be overridden by subclasses or 
        through instance-specific attributes.

        """
        return value

    def _format(self, value):
        """ The default method to format the given value to a unicode
        string for display. This may be overridden by subclasses or 
        through instance-specific attributes.

        """
        return unicode(value)

    def _validate(self, text):
        """ An internal validation method which returns a tuple of
        information related to the validation.

        This method is useful for subclasses to eliminate redundant 
        coercion code in the validate method.

        Parameters
        ----------
        text : unicode string
            The input string supplied by the user.
        
        Returns
        -------
        result : 2-tuple
            A 2-tuple of (<validation_result>, <value|None>). If the
            conversion and coercion are successful, then the first item 
            will be the ACCEPTABLE constant and the second item will be 
            the converted and coerced value. Otherwise, the first item 
            will be the INVALID constant and the second item will be None.
        
        """
        try:
            value = self._convert(text)
        except Exception:
            return (self.INVALID, None)
        
        try:
            value = self._coerce(value)
        except Exception:
            return (self.INVALID, None)
        
        return (self.ACCEPTABLE, value)
    
    def validate(self, text):
        """ Validates the input text against the rules of the validator.

        Parameters
        ----------
        text : unicode string
            The input string supplied by the user.
        
        Returns
        -------
        result : int
            One of the class attribute constants INVALID or ACCEPTABLE.
        
        Notes
        -----
        The string is INVALID under the following conditions:
            - The string fails to convert.
            - The converted value fails to coerce.
            - The coerced value is not the proper type.

        The string is ACCEPTABLE for all other conditions.

        """
        return self._validate(text)[0]

    def convert(self, text):
        """ Converts the user input text into an appropriate value or
        raises a ValueError if the conversion fails.

        This method is called only if the 'validate' method returns the
        ACCEPTABLE class attribute constant.

        Parameters
        ----------
        text : unicode string
            The input string supplied by the user.

        Returns
        -------
        result : object
            An appropriately converted object.
        
        """
        try:
            return self._coerce(self._convert(text))
        except Exception as e:
            msg = "Failed to convert %r. Original exception was %s."
            raise ValueError(msg % (text, e))

    def format(self, value):
        """ Convert the input value into a string which is appropriate
        for display.

        Parameters
        ----------
        value : object
            The context-dependent input value

        Returns
        -------
        result : unicode string
            A formatted unicode string for display.

        """
        return unicode(self._format(value))

    def normalize(self, text):
        """ Attempts to normalize the given text by converting it to the 
        numeric form, then back to unicode using the formatter. Returns 
        the original text if the conversion fails.

        """
        try:
            return self.format(self._coerce(self._convert(text)))
        except Exception:
            return text

