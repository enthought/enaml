#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_layout_component import QtLayoutComponent

from ..control import AbstractTkControl


class QtControl(QtLayoutComponent, AbstractTkControl):
    pass

