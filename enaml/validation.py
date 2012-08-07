#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import re

from traits.api import HasTraits, Str, Unicode, Property, cached_property


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

    #: A read only cached property which returns the compiled regex.
    _compiled_regex = Property(depends_on='regex')

    @cached_property
    def _get__compiled_regex(self):
        """ The getter for the '_compiled_regex' property. 

        Returns
        -------
        result : SRE_Pattern
            The compiled regular expression object to use for matching.

        """
        return re.compile(self.regex, re.UNICODE)

    def validate(self, text, component):
        """ Validates the text against the stored regular expression.

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
            The original edited text, and whether or not that text
            matched the regular expression.

        """
        return (text, bool(self._compiled_regex.match(text)))

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

