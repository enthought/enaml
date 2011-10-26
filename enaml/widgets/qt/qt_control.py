#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_component import QtComponent

from ..control import AbstractTkControl


class QtControl(QtComponent, AbstractTkControl):
    pass

