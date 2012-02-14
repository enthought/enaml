#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_constraints_widget import WXConstraintsWidget

from ...components.control import AbstractTkControl


class WXControl(WXConstraintsWidget, AbstractTkControl):
    pass

