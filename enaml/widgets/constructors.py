#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..toolkit import Constructor


def null_abstract_loader():
    return None


def include_shell_loader():
    from .include import Include
    return Include


CONSTRUCTORS = (
    ('Include', Constructor(include_shell_loader, null_abstract_loader)),
)

