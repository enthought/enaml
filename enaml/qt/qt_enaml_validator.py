#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QValidator


class QtEnamlValidator(QValidator):
    """ A QValidator implementation which proxies the work to the given
    Enaml validator.

    """
    def __init__(self, validator):
        """ Initialize a QtFieldValidator

        Parameters
        ----------
        validator : AbstractValidator
            An instance of the Enaml AbstractValidator.

        """
        super(QtEnamlValidator, self).__init__()
        self.validator = validator

    def validate(self, text, pos):
        """ Validates the given text using the 'validate' method of 
        Enaml validator.

        """
        v = self.validator
        rv = v.validate(text)
        if rv == v.ACCEPTABLE:
            res = QValidator.Acceptable
        elif rv == v.INTERMEDIATE:
            res = QValidator.Intermediate
        elif rv == v.INVALID:
            res = QValidator.Invalid
        else:
            # This should never happen
            raise ValueError('Invalid validation result')
        return (res, text, pos)
    
    def fixup(self, text):
        """ Attempts to fixup the given text using the 'normalize' method
        of the Enaml validator.

        """
        return self.validator.normalize(text)

