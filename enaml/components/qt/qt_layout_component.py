#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_component import QtComponent
from .qt_sizable import QtSizable
from .qt_stylable import QtStylable

from ..layout_component import AbstractTkLayoutComponent


class QtLayoutComponent(QtComponent, QtSizable, QtStylable,
                        AbstractTkLayoutComponent):
    """ A Qt4 implementation of LayoutComponent.

    """
    pass

