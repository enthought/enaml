#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_component import WXComponent

from ..control import AbstractTkControl


class WXControl(WXComponent, AbstractTkControl):
    pass
