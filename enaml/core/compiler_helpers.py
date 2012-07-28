#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .declarative import Declarative


def _make_decl_subclass(name, base, builder):
    """ A helper function for creating a new subtype.

    This function will raise an exception if the base type is of the
    incorrect type.

    Parameters
    ----------
    name : str
        The name to use when generating the new type.

    base : Declarative
        The base class to use for the new type. This must be a subclass
        of Declarative.

    builder : FunctionType
        The builder function created by the Enaml compiler. This 
        function will be used during instantiation to populate new
        instances with children and expressions.

    Returns
    -------
    result : type
        A new subclass of the given base class.

    """
    dct = {'__module__': builder.__module__, '__doc__': builder.__doc__}
    if not isinstance(base, type) or not issubclass(base, Declarative):
        msg = "can't derive enamldef from '%s'"
        raise TypeError(msg % base)
    decl_cls = type(name, (base,), dct)
    # Create a new builders list by placing this builder after the
    # builders of the base class, creating a builder "mro" of sorts.
    decl_cls._builders = base._builders + [builder]
    return decl_cls

