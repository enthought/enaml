#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import MetaHasTraits


class EnamlDef(MetaHasTraits):
    """ The type of an enamldef.

    This is a metaclass used to create types for the 'enamldef' keyword.
    Aside from a redefined __repr__ method, this type contains no logic.
    It exists to allow users to distinguish between normal classes and
    those which have be created by an enamldef keyword.

    All of the logic for handling the builder functions created by the
    Enaml compiler is included on the base Declarative class.
    
    """
    def __repr__(cls):
        return "<enamldef '%s.%s'>" % (cls.__module__, cls.__name__)

