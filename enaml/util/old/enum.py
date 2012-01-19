#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class EnumMeta(type):
    """ The metaclass for Enum which supplies the class name and 
    attribute name to Constant instances and places them in a dict 
    at __values__. A tuple of names for the constants are placed at 
    __names__ in sorted order. The constants themselves are placed
    in a set at __values_set__.

    """
    def __call__(cls, *args, **kwargs):
        raise RuntimeError('Cannot instantiate an Enum.')
    
    def __setattr__(cls, name, val):
        raise AttributeError('Cannot change the value of an Enum.')


class Enum(object):
    
    __metaclass__ = EnumMeta

    @classmethod
    def values(cls):
        """ Yields the values defined on the enum class.

        """
        for name in dir(cls):
            val = getattr(cls, name)
            if isinstance(val, int):
                yield val
    
    @classmethod
    def names(cls):
        """ Yields the names defined on the enum class.

        """
        for name in dir(cls):
            val = getattr(cls, name)
            if isinstance(val, int):
                yield name

    @classmethod
    def items(cls):
        """ Yields the items defined on the enum class.

        """
        for name in dir(cls):
            val = getattr(cls, name)
            if isinstance(val, int):
                yield name, val

