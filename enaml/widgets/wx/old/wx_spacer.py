#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from traits.api import implements, Instance

from .wx_control import WXControl
from ..spacer import ISpacerImpl


class WXSpacer(WXControl):

    implements(ISpacerImpl)
    
    widget = Instance(wx.Size)

    def create_widget(self):
        self.widget = wx.Size(*self.parent.size)

    def initialize_widget(self):
        pass
    
    def parent_size_changed(self, size):
        pass

