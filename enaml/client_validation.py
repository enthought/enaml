#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Client-side validation helpers for Python-based clients.

"""
def null_validator(text):
    """ A null validator function which accepts all input as valid.

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
        A callable which returns the original text if it matches the
        regex, or raises a ValueError if it doesn't.

    """
    import re
    rgx = re.compile(regex, re.UNICODE)
    def validator(text):
        return bool(rgx.match(text))
    return validator


def make_validator(info):
    """ Create a validator function for the given validator dict.

    Parameters
    ----------
    info : dict
    	The dictionary represenation of the validator sent by the
    	Enaml widget.

    Returns
    -------
    result : callable
    	A callable that will return True if th text input is valid,
    	False otherwise. If the given validator type is not supported,
    	then the null validator is returned.
    
    """
    vtype = info['type']
    if vtype == 'null':
        vldr = null_validator
    elif vtype == 'regex':
        vldr = regex_validator(info['arguments']['regex'])
    else:
        vldr = null_validator
    return vldr

