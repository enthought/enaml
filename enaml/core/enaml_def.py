#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import AtomMeta


class EnamlDef(AtomMeta):
    """ The type of an enamldef.

    This is a metaclass used to create types for the 'enamldef' keyword.
    The metaclass serves primarily to distinguish between types created
    by 'enamldef' and those created by traditional subclassing.

    """
    def __repr__(cls):
        """ A nice repr for a type created by the `enamldef` keyword.

        """
        return "<enamldef '%s.%s'>" % (cls.__module__, cls.__name__)

