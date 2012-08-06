#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Str, Unicode, ReadOnly


class Validator(HasTraits):
    """ The base class of all validator objects in Enaml.

    """
    #: The type of the validator to create on the client side. This
    #: value should be redefined by subclasses. The default type is
    #: 'null' and indicates that all edit text is considered valid.
    validator_type = ReadOnly('null')

    #: An optional message to associate with a validator. The client
    #: widget may use this to display a custom message if client-side
    #: validation fails.
    message = Unicode

    def as_dict(self):
        """ Returns a representation of the validator as dict.

        Returns
        -------
        result : dict
            A dictionary representation of the validator the conforms
            to the format specified in 'validator_format.js'.

        """
        res = {}
        res['type'] = self.validator_type
        res['message'] = self.message
        res['arguments'] = self.arguments()
        return res

    def arguments(self):
        """ Returns the arguments for the validator. 

        This method should be overridden by subclasses to return the
        appropriate arguments dict for the validator.

        Returns
        -------
        result : dict
            The dictionary of client-side validator arguments.

        """
        return {}

    def validate(self, orig_text, edit_text, edit_valid):
        """ A method that can be implemented by subclasses to perform
        additional server-side validation.

        This method is called every time the client widget sends the
        server widget a text edit event.

        Parameters
        ----------
        orig_text : unicode
            The original text in the Field. This will be the same as
            the current value of the 'text' attribute in the Field.

        edit_text : unicode
            The unicode text edited in the client widget.

        edit_valid : bool
            Whether or not the edit text passed client-side validation.

        Returns
        -------
        result : (unicode, bool)
            The (optionally modified) edit text and whether or not that
            text is considered valid. The default implementation returns 
            the given values with no modification.

        """
        return (edit_text, edit_valid)


class RegexValidator(Validator):
    """ A validator which validates based on a regular expression.

    """
    #: The type of the validator.
    validator_type = 'regex'
    
    #: The regular expression string to use for matching text.
    regex = Str

    def arguments(self):
        """ Returns the arguments dict for the client-side validator.

        """
        return {'regex': self.regex}

