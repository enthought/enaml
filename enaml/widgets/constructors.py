#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..toolkit import Constructor


def include_shell():
    from .include import Include
    return Include


def include_abstract():
    return None


CONSTRUCTORS = (
    ('Include', Constructor(include_shell, include_abstract)),
)

