#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_layout_component import WXLayoutComponent

from ..control import AbstractTkControl


class WXControl(WXLayoutComponent, AbstractTkControl):
    pass
