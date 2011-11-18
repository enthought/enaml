#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_container import QtContainer

from ..form import AbstractTkForm


class QtForm(QtContainer, AbstractTkForm):
    """ A Qt4 implementation of Container.

    """
    # The QtContainer implementation is enough.
    pass

