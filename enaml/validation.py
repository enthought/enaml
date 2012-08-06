#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Str, ReadOnly


class Validator(HasTraits):
    """ The base class of all validator objects in Enaml.

    """
    #: The type of the validator to create on the client side. This
    #: should be defined by subclasses.
    validator_type = ReadOnly('null')

    #: An optional message to associate with a validator. The client
    #: control may use this to display a custom message if and when
    #: the client-side validation fails.
    message = Str

    #: The pseudo state to apply to client field if the validator fails.
    fail_state = Str

    #: The pseudo state to apply to the client field if the succeeds.
    pass_state = Str

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
        res['fail_state'] = self.fail_state
        res['pass_state'] = self.pass_state
        res['arguments'] = self.arguments()

    def arguments(self):
        """ Returns the arguments for the validator. 

        This method should be overridden by subclasses to return the
        appropriate arguments dict.

        Returns
        -------
        result : dict
            The dictionary of client-side validator arguments.

        """
        return {}


class RegexValidator(Validator):
    """ A validator which validates based on a regular expression.

    """
    def __init__(self, regex, message='', fail_state=''):
        """ Initialize a RegexValidator.

        Parameters
        ----------
        regex : str
            A regular expression string to use for validating the 
            user's text input.

        """
