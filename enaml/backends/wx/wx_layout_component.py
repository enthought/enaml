#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_component import WXComponent
from .wx_sizable import WXSizable
from .wx_stylable import WXStylable

from ..layout_component import AbstractTkLayoutComponent


class WXLayoutComponent(WXComponent, WXSizable, WXStylable,
                        AbstractTkLayoutComponent):
    """ A Wx implementation of LayoutComponent.

    """
    pass

