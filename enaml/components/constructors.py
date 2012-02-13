#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..core.constructor import Constructor


def include_shell():
    from .include import Include
    return Include


def inline_shell():
    from .inline import Inline
    return Inline


CONSTRUCTORS = (
    ('Include', Constructor(include_shell)),
    ('Inline', Constructor(inline_shell)),
)

