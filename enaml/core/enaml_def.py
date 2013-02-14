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
    # Seed the class hierarchy with an empty descriptions tuple. The
    # compiler helper will add to this tuple when a new subclass is
    # created. The content will be 2-tuples of (description, globals)
    # which are the description dicts and the global scope for that
    # dict created by the enaml compiler.
    __enamldef_descriptions__ = ()

    def __repr__(cls):
        """ A nice repr for a type created by the `enamldef` keyword.

        """
        return "<enamldef '%s.%s'>" % (cls.__module__, cls.__name__)

