#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import re

from traits.api import Str, Property, cached_property

from .validator import Validator


class RegexValidator(Validator):
    """ A concrete Validator which handles text input.

    This validator ensures that the text matches a provided regular
    expression string.

    """
    #: The regular expression string to use for validation. The default
    #: regex matches everything.
    regex = Str(r'.*')

    #: A read only cached property which holds the compiled regular
    #: expression object.
    _regex = Property(depends_on='regex')

    @cached_property
    def _get__regex(self):
        """ The getter for the '_regex' property. 

        Returns
        -------
        result : sre object
            A compiled regular expression object for the current regex
            string.

        """
        return re.compile(self.regex, re.UNICODE)

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
        return (text, bool(self._regex.match(text)))

    def client_validator(self):
        """ The client side regex validator.

        Returns
        -------
        result : dict
            The dict representation of the client side regex validator.
            
        """
        res = {}
        res['type'] = 'regex'
        res['message'] = self.message
        res['arguments'] = {'regex': self.regex}
        return res

