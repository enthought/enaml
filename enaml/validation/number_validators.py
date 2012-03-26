#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ast import literal_eval
from numbers import Number, Real, Integral, Complex

from .coercing_validator import CoercingValidator


#------------------------------------------------------------------------------
# Base Number Validator
#------------------------------------------------------------------------------
class NumberValidator(CoercingValidator):
    """ A CoercingValidator subclass which accepts number strings which 
    will be converted using the builtin Python number types.

    """
    #: The type of the number to which the string must evaluate to be
    #: considered for validity.
    number_type = Number

    def __init__(self, low=None, high=None, precision=-1, **kwargs):
        """ Initialize a NumberValidator.

        Parameters
        ----------
        low : Number or None, optional
            The lowest acceptable value for the number. If None, there
            is no lower limit to the value. The default is None.
        
        high : Number or None, optional
            The highest acceptable value for the number. If None, there
            is no upper limit to the value. The default is None.

        precision : integer, optional
            An optional integer to control the precision of floating
            point number formatting. The default is -1 and indicates
            that implementation default precision should be used.

        **kwargs
            The keyword arguments necessary to initialize an instance
            of CoercingValidator.

        """
        super(NumberValidator, self).__init__(**kwargs)
        self.low = low
        self.high = high
        self.precision = precision

    def _convert(self, text):
        """ Overridden default convert method which uses the function
        ast.literal_eval to safetly evaluate the text. 
        
        Subclasses may override this to provide locale-aware text 
        conversion.

        """
        return literal_eval(text)

    def _post_convert_fail(self, text):
        """ A method intended to be overridden by subclasses which is
        called when conversion of the text fails. Such a failure would
        normally consider the input as INVALID. However, if this method
        returns True, then the text will be considered INTERMEDIATE. This
        is useful to handle cases where, for example, scientific notation
        is being entered and the trailing [eE][+-]? characters cause
        conversion to fail.

        Returns
        -------
        result : bool
            True if the failing text should be considered INTERMEDIATE,
            False otherwise.

        """
        return False

    def validate(self, text):
        """ Validates the input text against the rules of the validator.

        Parameters
        ----------
        text : unicode string
            The input string supplied by the user.
        
        Returns
        -------
        result : int
            One of the class attribute constants INVALID, INTERMEDIATE, 
            or VALID.
        
        Notes
        -----
        The string is INVALID under the following conditions:
            - The string fails coercing validation.
        
        The string is INTERMEDIATE under the following conditions:
            - The string is empty.
            - The coerced value is less than the low value.
            - The coerced value is greater than the high value.

        The string is ACCEPTABLE for all other situations.

        """
        if not text:
            return self.INTERMEDIATE

        validity, value = self._validate(text)
        if validity == self.INVALID:
            if self._post_convert_fail(text):
                validity = self.INTERMEDIATE
            return validity
            
        if not isinstance(value, self.number_type):
            return self.INVALID

        low = self.low
        if low is not None:
            if value < low:
                if value < 0:
                    return self.INVALID
                else:
                    return self.INTERMEDIATE
        
        high = self.high
        if high is not None:
            if value > high:
                if value > 0:
                    return self.INVALID
                else:
                    return self.INTERMEDIATE
        
        return self.ACCEPTABLE


class _PostConvertMixin(object):
    """ A validator mixin class which provides a post convert fail method
    which validates failing text based on given endings.

    """
    valid_fail_endings = ()

    def _post_convert_fail(self, text):
        """ Validates failing text based on the endings provided in the
        'valid_fail_endings' iterable.

        """
        for ending in self.valid_fail_endings:
            if text == ending:
                return True
            if text.endswith(ending):
                new = text[:-len(ending)]
                validity, value = self._validate(new)
                if validity != self.INVALID:
                    return True
        return False


#------------------------------------------------------------------------------
# numbers.Number Validators
#------------------------------------------------------------------------------
class IntegralNumberValidator(NumberValidator):
    """ A NumberValidator for Integral number types using the abstract 
    base class numbers.Integral for type checking.

    """
    number_type = Integral


class RealNumberValidator(_PostConvertMixin, NumberValidator):
    """ A NumberValidator for Real number types using the abstract 
    base class numbers.Real for type checking.

    """
    number_type = Real

    valid_fail_endings = (u'-', u'e', u'E', u'e+', u'E+', u'e-', u'E-')


class ComplexNumberValidator(NumberValidator):
    """ A NumberValidator for Complex number types using the abstract 
    base class numbers.Complex for type checking.

    """
    number_type = Complex

    def _post_convert_fail(self, text):
        """ A post convert fail method which allows trailing '+' and
        '-' symbols, as well scientific notation and missing 'j' 
        characters.

        """
        if text == u'-':
            return True

        if text.endswith(u'+') and text != u'+':
            new = text[:-1]
        elif u'+' in text and not text.endswith(u'j'):
            new = text + u'j'
        else:
            new = text
        
        validity, value = self._validate(new)
        if validity != self.INVALID:
            return True
        
        # If the text is still invalid, we may be entering trailing
        # scientific notation which we explicitly allow. Rather than 
        # ignoring the symbols, we attempt to complete them by adding
        # a 0 exponential. This makes the substitution position aware.
        for sub in (u'e+', u'e-', u'E+', u'E-', u'e', u'E'):
            subbed = new.replace(sub, sub + u'0')
            validity, value = self._validate(subbed)
            if validity != self.INVALID:
                return True
        
        return False


#------------------------------------------------------------------------------
# Concrete Number Validators
#------------------------------------------------------------------------------
class IntValidator(IntegralNumberValidator):
    """ A NumberValidator for 'int' number types which uses the given
    locale object to perform conversion.

    """
    number_type = int

    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_int(value, group=True)

    def _convert(self, text):
        """ Overridden default convert method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_int(text)


class LongValidator(IntegralNumberValidator):
    """ A NumberValidator for 'long' number types which uses the given
    locale object to perform conversion.

    """
    number_type = long

    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_long(value, group=True)

    def _convert(self, text):
        """ Overridden default convert method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_long(text)


class FloatValidator(RealNumberValidator):
    """ A NumberValidator for 'float' number types which uses the given
    locale object to perform conversion.

    """
    number_type = float

    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_float(value, group=True, prec=self.precision)

    def _convert(self, text):
        """ Overridden default convert method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_float(text)


class ComplexValidator(ComplexNumberValidator):
    """ A NumberValidator for 'complex' number types which uses the 
    given locale object to perform conversion.

    """
    number_type = complex

    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_complex(value, prec=self.precision)

    def _convert(self, text):
        """ Overridden default convert method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_complex(text)


class BinValidator(IntValidator):
    """ An IntValidator which converts and displays as a binary string
    and uses the given locale object to perform conversion.

    """
    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_int(value, base=2)

    def _convert(self, text):
        """ Overridden default convert method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_int(text, base=2)


class OctValidator(IntValidator):
    """ An IntValidator which converts and displays as an octal string
    and uses the given locale object to perform conversion.

    """
    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_int(value, base=8)

    def _convert(self, text):
        """ Overridden default convert method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_int(text, base=8)


class HexValidator(_PostConvertMixin, IntValidator):
    """ An IntValidator which converts and displays as a hex string
    and uses the given locale object to perform conversion.

    """
    valid_fail_endings = (u'0x', u'0X')

    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_int(value, base=16)

    def _convert(self, text):
        """ Overridden default convert method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_int(text, base=16)


class LongBinValidator(LongValidator):
    """ A LongValidator which converts and displays as a binary string
    and uses the given locale object to perform conversion.

    """
    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_long(value, base=2)

    def _convert(self, text):
        """ Overridden default converts method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_long(text, base=2)


class LongOctValidator(LongValidator):
    """ A LongValidator which converts and displays as an octal string
    and uses the given locale object to perform conversion.

    """
    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_long(value, base=8)

    def _convert(self, text):
        """ Overridden default convert method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_long(text, base=8)


class LongHexValidator(_PostConvertMixin, LongValidator):
    """ A LongValidator which converts and displays as a hex string
    and uses the given locale object to perform conversion.

    """
    valid_fail_endings = (u'0x', u'0X')

    def _format(self, value):
        """ Overridden default format method which uses the provided
        locale object to perform the formatting.

        """
        return self.locale.from_long(value, base=16)

    def _convert(self, text):
        """ Overridden default convert method which uses the provided
        locale object to perform the conversion.

        """
        return self.locale.to_long(text, base=16)

