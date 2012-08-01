#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.utils import log_exceptions

import wx
import wx.lib.

class wxRouter(wx.EvtHandler):
    """ A simple wx.EvtHandler subclass which assists in routing 
    messages in a deferred fashion.

    This object emits three events:


    """