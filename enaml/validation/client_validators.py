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
from functools import partial

def null_preprocessor(**kwargs):
    """ A validator preprocessor which does no preprocessing.
    
    Parameters
    ----------
    **kwargs : 
        The arguments passed to the validator
    
    Returns
    -------
    kwargs :
        A modified set of kwargs to be passed to the closure.
    
    """
    return kwargs

def null_validator(text):
    """ A validator function will returns True for all text input.

    Parameters
    ----------
    text : string
        The text to validate.

    """
    return True


def regex_preprocessor(regex=r'.*'):
    """ A validator preprocessor which does no preprocessing.
    
    Parameters
    ----------
    regex : 
        The regex string to match
    
    Returns
    -------
    kwargs :
        A dictionary containing the compiled regular expression.
    
    """
    return {'regex': re.compile(regex, re.UNICODE)}


def regex_validator(text, regex):
    """ Creates a callable which will validate text input against the
    provided regex string.

    Parameters
    ----------
    text : string
        The text to validate.

    regex : compiled regular expression
        A regular expression to use for matching.

    Returns
    -------
    results : callable
        A callable which returns True if the text matches the regex,
        False otherwise.

    """
    return bool(regex.match(text))


def int_range_validator(text, base=10, minimum=None, maximum=None):
    """ Creates a callable which will validate text input against the
    provided integer range.

    Parameters
    ----------
    text : string
        The text to validate.

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
        A callable which returns True if the text matches the range,
        False otherwise.

    """
    try:
        value = int(text, base)
    except ValueError:
        return False
        
    if minimum is not None and value < minimum:
        return False
    if maximum is not None and value > maximum:
        return False
    return True


def float_range_validator(text, minimum=None, maximum=None, precision=None,
        allow_exponent=False):
    """ Creates a callable which will validate text input against the
    provided float range.

    Parameters
    ----------
    text : string
        The text to validate.

    minimum : None or int
        The base 10 lower bound of allowable values, inlcusive. None 
        indicates no lower bound.

    maximum : None or int
        The base 10 upper bound of allowable values, inlcusive. None 
        indicates no upper bound.
    
    precision : None or int
        The number of places to allow after the decimal point.  None
        indicates arbitrary precision.

    allow_exponent : bool
        Whether or not to allow exponents like '1e6' in the input.

    Returns
    -------
    results : callable
        A callable which returns True if the text matches the range,
        False otherwise.

    """
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


# Client validator look-up table

validator_types = {
    'regex': (regex_preprocessor, regex_validator),
    'int_range': (null_preprocessor, int_range_validator),
    'float_range': (null_preprocessor, float_range_validator),
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
        preprocessor, validator = validator_types[vtype]
        arguments = preprocessor(**info['arguments'])
        return partial(validator, **arguments)
    else:
        return null_validator
