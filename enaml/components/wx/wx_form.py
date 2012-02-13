#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_container import WXContainer

from ..form import AbstractTkForm


class WXForm(WXContainer, AbstractTkForm):
    """ A wxPython implementation of Container.

    """
    # The WXContainer implementation is enough.
    pass

