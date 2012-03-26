#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from numbers import Real, Integral, Complex

from .number_validators import NumberValidator


class NumberExpressionSandboxError(RuntimeError):
    """ A RuntimeError subclass indicating a sandbox access violation.

    """
    pass


class NumberExpressionSandbox(object):
    """ A simple sandbox for us with NumberValidator that does allow 
    name access.

    """
    allowed = {
        'int': int, 'float': float, 'long': long, 'complex': complex,
    }

    def __getitem__(self, name):
        allowed = self.allowed
        if name not in allowed:
            msg = "Expression sandbox does not allow access to '%s'" % name
            raise NumberExpressionSandboxError(msg)
        return allowed[name]

    def __setitem__(self, name, value):
        msg = "Expression sandbox does not allow writes"
        raise NumberExpressionSandboxError(msg)


class NumberExpressionValidator(NumberValidator):
    """ A NumberValidator subclass that accepts a string expression 
    which evaluates to a Python number. 

    The string evaluation is performed in a sandboxed environment which
    allows limited access to Python builtins. Locale information is not
    used for formatting or conversion.

    """
    #: The sandbox in which the input string will be evaluated. This 
    #: should typically not be manipulated by user code, lest ye 
    #: suffer the security vulnerabilities.
    sandbox = ({'__builtins__': {}}, NumberExpressionSandbox())

    def _convert(self, text):
        """ Overridden default convert method which safetly evaluates 
        the given string in a sandboxed environment. 

        It does not use the locale object to perform conversion since 
        it allows for generic arithmetic expressions which must make
        a successful round-trip.

        """
        return eval(text, *self.sandbox)
        
    def _coerce(self, value):
        """ Overriden default coerce method which attempts to use the
        number type to coerce the value if it is not already of the
        proper type.

        """
        if not isinstance(value, self.number_type):
            try:
                value = self.number_type(value)
            except (TypeError, ValueError):
                pass
        return value

    def validate(self, text):
        """ Overridden default validator which converts any INVALID
        result into INTERMEDIATE. This allows arbitrary expresssions
        to be entered into the field.

        """
        v = super(NumberExpressionValidator, self).validate(text)
        if v == self.INVALID:
            v = self.INTERMEDIATE
        return v


class IntegralNumberExpressionValidator(NumberExpressionValidator):
    """ A NumberExpressionValidator for Integral number types using the
    abstract base class numbers.Integral for type checking.

    """
    number_type = Integral


class RealNumberExpressionValidator(NumberExpressionValidator):
    """ A NumberExpressionValidator for Real number types using the 
    abstract base class numbers.Real for type checking.

    """
    number_type = Real


class ComplexNumberExpressionValidator(NumberExpressionValidator):
    """ A NumberExpressionValidator for Complex number types using the 
    abstract base class numbers.Complex for type checking.

    """
    number_type = Complex


class IntExpressionValidator(IntegralNumberExpressionValidator):
    """ A NumberExpressionValidator for 'int' number types.

    """
    number_type = int


class LongExpressionValidator(IntegralNumberExpressionValidator):
    """ A NumberExpressionValidator for 'long' number types.

    """
    number_type = long


class FloatExpressionValidator(RealNumberExpressionValidator):
    """ A NumberExpressionValidator for 'float' number types.

    """
    number_type = float


class ComplexExpressionValidator(ComplexNumberExpressionValidator):
    """ A NumberExpressionValidator for 'complex' number types.

    """
    number_type = complex


class BinExpressionValidator(IntExpressionValidator):
    """ An IntExpressionValidator which formats as a binary string.

    """
    def _format(self, value):
        """ Overridden default format method to format as a binary
        string.

        """
        return bin(value)


class OctExpressionValidator(IntExpressionValidator):
    """ An IntExpressionValidator which formats as an octal string.

    """
    def _format(self, value):
        """ Overridden default format method to format as an octal
        string.

        """
        return oct(value)


class HexExpressionValidator(IntExpressionValidator):
    """ An IntExpressionValidator which formats as a hex string.

    """
    def _format(self, value):
        """ Overridden default format method to format as a hex
        string.

        """
        return hex(value)


class LongBinExpressionValidator(LongExpressionValidator):
    """ A LongExpressionValidator which formats as a binary string.

    """
    def _format(self, value):
        """ Overridden default format method to format as a binary
        string.

        """
        return bin(value)


class LongOctExpressionValidator(LongExpressionValidator):
    """ A LongExpressionValidator which formats as an octal string.

    """
    def _format(self, value):
        """ Overridden default format method to format as an octal
        string.

        """
        return oct(value)


class LongHexExpressionValidator(LongExpressionValidator):
    """ A LongExpressionValidator which formats as a hex string.

    """
    def _format(self, value):
        """ Overridden default format method to format as a hex
        string.

        """
        return hex(value)

