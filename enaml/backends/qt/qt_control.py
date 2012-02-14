#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_constraints_widget import QtConstraintsWidget

from ...components.control import AbstractTkControl


class QtControl(QtConstraintsWidget, AbstractTkControl):
    """ A Qt4 implementation of Control.

    """
    pass

