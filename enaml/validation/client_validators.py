#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
"""
Python implementation of basic validation
-----------------------------------------

These are intended to be a single location for the Python implementation of
client-side validators.  Implementations in other languages (eg. javascript)
or in tookits which provide their own validation system should use these as
references.

"""

import re

def null_validator(text):
    """ A validator function will returns True for all text input.

    """
    return True


def regex_validator(regex):
    """ Creates a callable which will validate text input against the
    provided regex string.

    Parameters
    ----------
    regex : string
        A regular expression string to use for matching.

    Returns
    -------
    results : callable
        A callable which returns True if the text matches the regex,
        False otherwise.

    """
    rgx = re.compile(regex, re.UNICODE)
    def validator(text):
        return bool(rgx.match(text))
    return validator


def int_range_validator(base=10, minimum=None, maximum=None):
    """ Creates a callable which will validate text input against the
    provided regex string.

    Parameters
    ----------
    base : 2, 8, 10, or 16
        The number base to use with the range. Supported bases are 
        2, 8, 10, and 16.

    minimum : None or int
        The base 10 lower bound of allowable values, inlcusive. None 
        indicates no lower bound.

    maximum : None or int
        The base 10 upper bound of allowable values, inlcusive. None 
        indicates no upper bound.

    Returns
    -------
    results : callable
        A callable which returns True if the text matches the regex,
        False otherwise.

    """
    def validator(text):
        try:
            value = int(text, base)
        except ValueError:
            return False
        if minimum is not None and value < minimum:
            return False
        if maximum is not None and value > maximum:
            return False
        return True
    return validator


def float_range_validator(minimum=None, maximum=None, precision=None,
        allow_scientific_notation=False):
    """ Creates a callable which will validate text input against the
    provided regex string.

    Parameters
    ----------
    minimum : None or int
        The base 10 lower bound of allowable values, inlcusive. None 
        indicates no lower bound.

    maximum : None or int
        The base 10 upper bound of allowable values, inlcusive. None 
        indicates no upper bound.
    
    precision : None or int
        The number of places to allow after the decimal point.  None
        indicates arbitrary precision.

    allow_scientific_notation : bool
        Whether or not to allow scientific notation in the input.

    Returns
    -------
    results : callable
        A callable which returns True if the text matches the regex,
        False otherwise.

    """
    def validator(text):
        try:
            value = float(text)
        except ValueError:
            return False
        if minimum is not None and value < minimum:
            return False
        if maximum is not None and value > maximum:
            return False
        if precision is not None and value != round(value, precision):
            return False
        if not allow_scientific_notation and 'e' in text.lower():
            return False
        return True
    return validator


# Client validator look-up table

validator_types = {
    'regex': regex_validator,
    'int_range': int_range_validator,
    'float_range': float_range_validator,
}

#------------------------------------------------------------------------------
#  Client validator utilities
#------------------------------------------------------------------------------

def make_validator(info):
    """ Make a validator function for the given dict represenation.

    Parameters
    ----------
    info : dict
        The dictionary representation of a client side validator sent
        by the Enaml server widget.

    Returns
    -------
    result : callable
        A callable which will return True if the text is valid. False
        otherwise. If the validator type is not supported, a null 
        validator which accepts all text will be returned.
    
    """
    vtype = info['type']
    if vtype in validator_types:
        vldr = validator_types[vtype](**info['arguments'])
    else:
        vldr = null_validator
    return vldr
