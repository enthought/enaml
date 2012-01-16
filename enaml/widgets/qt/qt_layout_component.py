#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_component import QtComponent
from .qt_resizable import QtResizable
from .qt_stylable import QtStylable

from ..layout_component import AbstractTkLayoutComponent


class QtLayoutComponent(QtComponent, QtResizable, QtStylable,
                        AbstractTkLayoutComponent):
    """ A Qt4 implementation of LayoutComponent.

    """
    pass

